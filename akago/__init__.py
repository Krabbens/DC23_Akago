from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from beanie import init_beanie
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient

from akago.config import STATIC_DIR
from akago.dependencies.google import init_google_service
from akago.dependencies.templates import get_templates
from akago.models.form import Form
from akago.models.metadata import Metadata
from akago.models.request import AugmentationDocument
from akago.pdf.document import init_pdf_creator
from akago.pdf.metadata import get_metadata
from akago.routers import requests
from akago.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    init_google_service()
    init_pdf_creator()

    client = AsyncIOMotorClient(
        f"mongodb://{settings.db_username}:{settings.db_password}@localhost:27017/",
    )

    await init_beanie(database=client.documents, document_models=[AugmentationDocument])
    yield

    client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(requests.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root(
    request: Request,
    metadata: Annotated[Metadata, Depends(get_metadata)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
):
    context = {"form": Form.from_metadata(metadata).model_dump(mode="json")}

    return templates.TemplateResponse(request, "form.jinja", context)
