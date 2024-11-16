from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from beanie import init_beanie
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient

from akago.google import init_google_service
from akago.models.form import Form
from akago.models.metadata import Metadata
from akago.models.request import AugmentationDocument
from akago.pdf.metadata import get_metadata
from akago.routers import requests
from akago.settings import get_settings
from akago.templates import templates


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    client = AsyncIOMotorClient(
        f"mongodb://{settings.db_username}:{settings.db_password}@localhost:27017/",
    )

    init_google_service()
    await init_beanie(database=client.documents, document_models=[AugmentationDocument])
    yield

    client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(requests.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root(request: Request, metadata: Annotated[Metadata, Depends(get_metadata)]):
    context = {"form": Form.from_metadata(metadata).model_dump(mode="json")}

    return templates.TemplateResponse(request, "form.jinja", context)
