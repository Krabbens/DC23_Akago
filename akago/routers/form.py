import mimetypes
from io import BytesIO
from typing import Annotated
from uuid import uuid4

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from googleapiclient.http import MediaIoBaseUpload

from akago.camunda.camunda_rest_api import Camunda
from akago.dependencies.google import GoogleService, get_google_service
from akago.dependencies.templates import get_templates
from akago.models.form import Form
from akago.models.metadata import Metadata
from akago.models.request import (
    ActiveForm,
    AugmentationData,
    AugmentationDocument,
    PersonalData,
)
from akago.pdf.document import create_document
from akago.pdf.metadata import get_metadata

_PERSONAL_DATA_Y0: float = 350.0

router = APIRouter(prefix="/form")


async def _get_form(id: PydanticObjectId) -> ActiveForm:
    form = await ActiveForm.get(id)

    if form is None:
        raise HTTPException(status_code=404, detail="Invalid document ID")

    return form


@router.get("")
async def get_form(
    request: Request,
    metadata: Annotated[Metadata, Depends(get_metadata)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
):
    metadata.fields = list(
        filter(
            lambda field: field.position.page == 0
            and field.position.y0 <= _PERSONAL_DATA_Y0,
            metadata.fields,
        )
    )
    context = {"form": Form.from_metadata(metadata).model_dump(mode="json")}

    return templates.TemplateResponse(request, "personal_data_form.jinja", context)


@router.post("")
async def post_personal_data(personal_data: PersonalData):
    access_token = Camunda.genToken()
    access_token_operate = Camunda.genTokenOperate()
    camunda_process_id = Camunda.startProcessWithWebhook()

    task_id = None
    while task_id is None:
        task_id = Camunda.searchTaskForProcess(camunda_process_id, access_token)

    Camunda.sendRequest(task_id, "birthDate", personal_data.birthDate, access_token)

    is_completed = Camunda.is_process_completed(
        camunda_process_id, access_token_operate
    )
    task_name = Camunda.getTask(task_id, access_token)
    while task_name != "Wybór rodzaju wszczepu" and is_completed == False:
        is_completed = Camunda.is_process_completed(
            camunda_process_id, access_token_operate
        )
        task_id = Camunda.searchTaskForProcess(camunda_process_id, access_token)
        if task_id is not None:
            task_name = Camunda.getTask(task_id, access_token)

    print({task_name})
    if task_name != "Wybór rodzaju wszczepu":
        return Response(
            status_code=200,
            headers={"Location": "/form/invalid-age"},
        )
    else:
        form = await ActiveForm(
            camunda_process_id=str(camunda_process_id),
            personal_data=personal_data,
        ).insert()

        return Response(
            status_code=201,
            headers={
                "Location": f"/form/{form.id}",
            },
        )


@router.get("/invalid-age")
async def get_invalid_age(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
):
    return templates.TemplateResponse(request, "invalid_age.jinja")


@router.get("/{id}")
async def get_augmentation_form(
    request: Request,
    metadata: Annotated[Metadata, Depends(get_metadata)],
    form: Annotated[ActiveForm, Depends(_get_form)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
):
    metadata.fields = list(
        filter(
            lambda field: field.position.page > 0
            or field.position.y0 > _PERSONAL_DATA_Y0,
            metadata.fields,
        )
    )

    access_token = Camunda.genToken()

    implant_options = None
    while implant_options is None:
        task_id = Camunda.searchTaskForProcess(
            int(form.camunda_process_id), access_token
        )
        if task_id is not None:
            implant_options = Camunda.getTaskVariableValue(
                task_id, access_token, "implantOptions"
            )

    if implant_options:
        print(f"Wartość zmiennej implantOptions: {implant_options}")
        task_variable = Camunda.getTaskVariableValue(
            task_id, access_token, "implantOptions"
        )
        task_variable = [
            {
                "name" : option["value"].replace("-", " ").capitalize(),
                "value" : option["value"],
                "is_extra" : option["is_extra"]
            } for option in task_variable
        ]
        print(f"Wartość zmiennej task_variable: {task_variable}")
    context = {
        "form": Form.from_metadata(metadata).model_dump(mode="json"),
        "id": form.id,
        "augmentation_options": task_variable,
    }

    return templates.TemplateResponse(request, "augmentation_form.jinja", context)


@router.post("/{id}")
async def create_request(
    augmentation_data: AugmentationData,
    form: Annotated[ActiveForm, Depends(_get_form)],
    google: Annotated[GoogleService, Depends(get_google_service)],
):
    doc = create_document(form.personal_data, augmentation_data)

    filename = f"{uuid4()}.pdf"
    file_content = BytesIO(doc)
    media = MediaIoBaseUpload(file_content, mimetype=mimetypes.types_map[".pdf"])

    file_id = google.upload_file(filename, media)

    access_token = Camunda.genToken()

    task_id = None
    while task_id is None:
        task_id = Camunda.searchTaskForProcess(
            int(form.camunda_process_id), access_token
        )
    Camunda.sendRequest(task_id, "changeOfChoice", False, access_token)

    document = await AugmentationDocument(
        file_id=file_id,
        filename=filename,
        personal_data=form.personal_data,
        augmentation_data=augmentation_data,
    ).insert()

    return Response(
        status_code=201,
        headers={
            "Location": f"/requests/{document.id}",
        },
    )


@router.get("/{id}/options/{option}")
async def get_augmentation_options(
    request: Request,
    id: str,
    option: str,
    form: Annotated[ActiveForm, Depends(_get_form)],
):
    access_token = Camunda.genToken()

    task_id = None
    while task_id is None:
        task_id = Camunda.searchTaskForProcess(
            int(form.camunda_process_id), access_token
        )

    task_name = Camunda.getTask(task_id, access_token)

    if task_name != "Wybór rodzaju wszczepu":
        Camunda.sendRequest(task_id, "changeOfChoice", True, access_token)

        while task_name != "Wybór rodzaju wszczepu":
            task_id = Camunda.searchTaskForProcess(
                int(form.camunda_process_id), access_token
            )
            if task_id is not None:
                task_name = Camunda.getTask(task_id, access_token)

    Camunda.sendRequest(task_id, "type", option, access_token)

    while task_name == "Wybór rodzaju wszczepu":
        task_id = Camunda.searchTaskForProcess(
            int(form.camunda_process_id), access_token
        )
        if task_id is not None:
            task_name = Camunda.getTask(task_id, access_token)

    print({task_name})
    options = Camunda.getTaskVariableValue(task_id, access_token, "additionalOptions")

    if options:
        print(f"Dodatkowe opcje dla {option}: {options}")
    else:
        options = []

    return JSONResponse(options)
