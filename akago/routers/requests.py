import mimetypes
from email.message import EmailMessage
from io import BytesIO
from typing import Annotated
from uuid import uuid4

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from googleapiclient.http import MediaIoBaseUpload

from akago.google import GoogleService, get_google_service
from akago.models.request import AugmentationDocument, AugmentationRequest
from akago.pdf.document import create_document
from akago.settings import Settings, get_settings
from akago.templates import templates

router = APIRouter(prefix="/requests")


async def _get_document(id: PydanticObjectId) -> AugmentationDocument:
    document = await AugmentationDocument.get(id)

    if document is None:
        raise HTTPException(status_code=404, detail="Invalid document ID")

    return document


@router.post("")
async def create_request(
    augmentation_request: AugmentationRequest,
    google: Annotated[GoogleService, Depends(get_google_service)],
):
    doc = create_document(augmentation_request)

    filename = f"{uuid4()}.pdf"
    file_content = BytesIO(doc.tobytes())
    media = MediaIoBaseUpload(file_content, mimetype=mimetypes.types_map[".pdf"])

    file_id = google.upload_file(filename, media)

    document = await AugmentationDocument(
        file_id=file_id,
        filename=filename,
        email=augmentation_request.email,
        gender=augmentation_request.sex,
    ).insert()

    return Response(status_code=201, headers={"Location": f"/requests/{document.id}"})


@router.get("/{id}")
async def get_request(
    request: Request, document: Annotated[AugmentationDocument, Depends(_get_document)]
):
    context = {"id": document.id}

    return templates.TemplateResponse(request, "request.jinja", context)


@router.get("/{id}/download")
async def download_request(
    google: Annotated[GoogleService, Depends(get_google_service)],
    document: Annotated[AugmentationDocument, Depends(_get_document)],
):
    file = google.download_file(document.file_id)

    return Response(
        content=file,
        media_type=mimetypes.types_map[".pdf"],
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )


@router.post("/{id}/email")
async def email_request(
    settings: Annotated[Settings, Depends(get_settings)],
    google: Annotated[GoogleService, Depends(get_google_service)],
    document: Annotated[AugmentationDocument, Depends(_get_document)],
):
    file = google.download_file(document.file_id)
    maintype, subtype = mimetypes.types_map[".pdf"].split("/", maxsplit=1)
    message = EmailMessage()
    message["To"] = document.email
    message["From"] = settings.email
    message["Subject"] = "Wniosek o Personalizowaną Augmentację Cybernetyczną"

    message.set_content("TODO")
    message.add_attachment(
        file,
        filename=document.filename,
        maintype=maintype,
        subtype=subtype,
    )

    google.send_email(message)
