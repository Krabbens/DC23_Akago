import mimetypes
from email.message import EmailMessage
from textwrap import dedent
from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates

from akago.dependencies.google import GoogleService, get_google_service
from akago.dependencies.morfeusz import Analyzer, get_analyzer
from akago.dependencies.templates import get_templates
from akago.models.request import AugmentationDocument, Gender
from akago.settings import Settings, get_settings

router = APIRouter(prefix="/requests")


async def _get_document(id: PydanticObjectId) -> AugmentationDocument:
    document = await AugmentationDocument.get(id)

    if document is None:
        raise HTTPException(status_code=404, detail="Invalid document ID")

    return document


@router.get("/{id}")
async def get_request(
    request: Request,
    document: Annotated[AugmentationDocument, Depends(_get_document)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
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
    analyzer: Annotated[Analyzer, Depends(get_analyzer)],
):
    file = google.download_file(document.file_id)
    maintype, subtype = mimetypes.types_map[".pdf"].split("/", maxsplit=1)
    message = EmailMessage()
    message["To"] = document.personal_data.email
    message["From"] = settings.email
    message["Subject"] = "Wniosek o Personalizowaną Augmentację Cybernetyczną"

    message.set_content(_create_email_content(document, analyzer))
    message.add_attachment(
        file,
        filename=document.filename,
        maintype=maintype,
        subtype=subtype,
    )

    google.send_email(message)


def _create_email_content(document: AugmentationDocument, analyzer: Analyzer) -> str:
    dear_lemma = "szanowny"
    dear_tag: str
    person_lemma: str
    person_tag: str

    match document.personal_data.sex:
        case Gender.MALE:
            dear_tag = "adj:sg:nom.voc:m1.m2.m3:pos"
            person_lemma = "pan"
            person_tag = "subst:sg:voc:m1"
        case Gender.FEMALE:
            dear_tag = "adj:sg:nom.voc:f:pos"
            person_lemma = "pani"
            person_tag = "subst:sg:voc:f"
        case Gender.OTHER:
            dear_tag = "adj:pl:nom.voc:m1:pos"
            person_lemma = "państwo"
            person_tag = "subst:pl:nom.voc:m1:pt"

    content = f"""\
    {analyzer.inflect(dear_lemma, dear_tag).capitalize()} {analyzer.inflect(person_lemma, person_tag).capitalize()}!

    Serdecznie dziękujemy za złożenie Wniosku o Augmentację Cybernetyczną. Przesyłamy w załączniku
    niniejszej wiadomości wygenerowany dokument potwierdzający udział w procesie augmentacji.

    Życzymy miłego dnia

    Akago Systems Incorporated
    """

    return dedent(content)
