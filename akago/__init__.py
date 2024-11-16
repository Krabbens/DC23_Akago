from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from akago.models.form import Form
from akago.models.metadata import Metadata
from akago.pdf.metadata import get_metadata
from akago.routers import requests
from akago.templates import templates

app = FastAPI()

app.include_router(requests.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root(
    request: Request, metadata: Annotated[Metadata, Depends(get_metadata)]
) -> HTMLResponse:
    context = {"form": Form.from_metadata(metadata).model_dump(mode="json")}

    return templates.TemplateResponse(request, "form.jinja", context)
