import mimetypes
from io import BytesIO
from typing import Annotated
from uuid import uuid4

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from googleapiclient.http import MediaIoBaseUpload

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
    form = await ActiveForm(
        # TODO: Handle Camunda. If age is invalid, you can redirect with code 303 to `/form/invalid-age`.
        camunda_process_id="TODO-ID",
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
    context = {
        "form": Form.from_metadata(metadata).model_dump(mode="json"),
        # TODO: Get selectable options from Camunda.
        "augmentation_options": [
            {"value": "opt1", "is_extra": False},
            {"value": "opt2", "is_extra": True},
            {"value": "opt3", "is_extra": False},
        ],
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
    form: Annotated[ActiveForm, Depends(_get_form)],
    option: str,
):
    # TODO: Get augmentation options for the option `option` from Camunda.
    print(form.camunda_process_id, option)

    return JSONResponse(["option1", "option2", "option3"])
