import io
import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Optional
from xml.etree.ElementTree import Element, ElementTree

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rich import print


# FIXME: This class is inaccurate as it was made to handle receiving data from a browser. We should
# improve it when implementing the data validation task.
class OrderData(BaseModel):
    name: str
    birthDate: date
    gender: str
    idNumber: str
    address: str
    phoneEmail: str
    implantType: str
    implantPurpose: str
    estheticPreferences: str
    installationDate: date
    preferredFacility: str
    bloodGroup: str
    rh: str
    medicalHistory: Optional[str] = None
    implantHistory: Optional[str] = None
    medications: str
    dataConsent: bool
    installationConsent: bool
    marketingConsent: bool = False
    additionalRequirements: str


app = FastAPI()

app.mount("/static", StaticFiles(directory="public"), name="static")


@app.get("/", response_class=HTMLResponse)
def get_root():
    form_data = json.loads(Path("form.json").read_text())
    content = _generate_form(form_data)

    return HTMLResponse(content)


@app.post("/order")
def create_order(data: Annotated[OrderData, Form()]):
    print(data)

    return RedirectResponse("/", status_code=303)


def _generate_form(json: Any) -> str:
    html = Element("html", {"lang": "pl"})
    tree = ElementTree(html)
    head = ET.SubElement(html, "head")

    head.append(
        Element(
            "link",
            {
                "rel": "stylesheet",
                "href": "https://unpkg.com/sakura.css/css/sakura-dark.css",
                "media": "screen and (prefers-color-scheme: dark)",
            },
        )
    )

    body = ET.SubElement(html, "body")

    body.append(
        Element(
            "img",
            {
                "src": "/static/logo.png",
                "alt": "Logo",
                "width": "400",
                "height": "400",
                "style": "display: block; width: 100px; height: 100px; margin-inline: auto",
            },
        )
    )

    form = ET.SubElement(body, "form", {"action": "/order", "method": "post"})
    form_title = ET.SubElement(form, "h1")
    form_title.text = json["formTitle"]

    for section in json["sections"]:
        fieldset = ET.SubElement(form, "fieldset")
        legend = ET.SubElement(fieldset, "legend")
        legend.text = section["sectionTitle"]

        for field in section["fields"]:
            match field["type"]:
                case "text" | "date":
                    label = ET.SubElement(fieldset, "label", {"for": field["name"]})
                    label.text = field["label"]

                    field_attrs: dict[str, str] = {
                        "type": field["type"],
                        "id": field["name"],
                        "name": field["name"],
                        "placeholder": field.get("placeholder", ""),
                    }

                    # HTML requires false boolean attributes to be omitted. Empty string is treated
                    # as true.
                    if field.get("required", False):
                        field_attrs["required"] = ""

                    fieldset.append(Element("input", field_attrs))
                case "textarea":
                    label = ET.SubElement(fieldset, "label", {"for": field["name"]})
                    label.text = field["label"]

                    field_attrs: dict[str, str] = {
                        "id": field["name"],
                        "name": field["name"],
                        "placeholder": field.get("placeholder", ""),
                    }

                    if field.get("required", False):
                        field_attrs["required"] = ""

                    fieldset.append(Element("textarea", field_attrs))
                case "select":
                    label = ET.SubElement(fieldset, "label", {"for": field["name"]})
                    label.text = field["label"]

                    field_attrs: dict[str, str] = {
                        "id": field["name"],
                        "name": field["name"],
                    }

                    if field.get("required", False):
                        field_attrs["required"] = ""

                    select = ET.SubElement(fieldset, "select", field_attrs)

                    for option in field["options"]:
                        opt = ET.SubElement(select, "option", {"value": option})
                        opt.text = option
                case "multi-select":
                    label = ET.SubElement(fieldset, "label", {"for": field["name"]})
                    label.text = field["label"]

                    for option in field["options"]:
                        fieldset.append(
                            Element(
                                "input",
                                {
                                    "type": "checkbox",
                                    "id": option,
                                    "name": field["name"],
                                    "value": option,
                                },
                            )
                        )

                        label = ET.SubElement(fieldset, "label", {"for": option})
                        label.text = option

                        fieldset.append(Element("br"))
                case "checkbox":
                    field_attrs: dict[str, str] = {
                        "type": "checkbox",
                        "id": field["name"],
                        "name": field["name"],
                    }

                    if field.get("required", False):
                        field_attrs["required"] = ""

                    fieldset.append(Element("input", field_attrs))

                    label = ET.SubElement(fieldset, "label", {"for": field["name"]})
                    label.text = field["label"]

    form.append(Element("input", {"type": "submit", "value": "Zatwierdź"}))

    stream = io.StringIO()

    stream.write("<!DOCTYPE html>")
    tree.write(
        stream,
        encoding="unicode",
        method="html",
        xml_declaration=False,
        short_empty_elements=False,
    )

    return stream.getvalue()


# This is needed for debugging.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
