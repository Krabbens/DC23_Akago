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
from akago.models.request import ActiveForm, AugmentationDocument
from akago.pdf.document import init_pdf_creator
from akago.routers import form, requests
from akago.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    init_google_service()
    init_pdf_creator()

    client = AsyncIOMotorClient(
        f"mongodb://{settings.db_username}:{settings.db_password}@localhost:27017/",
    )

    await init_beanie(
        database=client.documents, document_models=[AugmentationDocument, ActiveForm]
    )
    yield

    client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(requests.router)
app.include_router(form.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
):
    return templates.TemplateResponse(request, "index.jinja")
