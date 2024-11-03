import io
import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Optional
from xml.etree.ElementTree import Element, ElementTree

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rich import print

from PyPDF2 import PdfReader, PdfWriter

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
    form_data = json.loads(Path("form.json").read_text(encoding='utf-8'))
    content = _generate_form(form_data)

    return HTMLResponse(content, media_type="text/html; charset=utf-8")


@app.post("/order")
def create_order(data: Annotated[OrderData, Form()]):
    print(data)

    return RedirectResponse("/", status_code=303)

@app.get("/download")
def download_pdf(request: Request):
    form_data = request.query_params
    order_data = OrderData(
        name=form_data.get("name", ""),
        birthDate=form_data.get("birthDate", ""),
        gender=form_data.get("gender", ""),
        idNumber=form_data.get("idNumber", ""),
        address=form_data.get("address", ""),
        phoneEmail=form_data.get("phoneEmail", ""),
        implantType=form_data.get("implantType", ""),
        implantPurpose=form_data.get("implantPurpose", ""),
        estheticPreferences=form_data.get("estheticPreferences", ""),
        installationDate=form_data.get("installationDate", ""),
        preferredFacility=form_data.get("preferredFacility", ""),
        bloodGroup=form_data.get("bloodGroup", ""),
        rh=form_data.get("rh", ""),
        medicalHistory=form_data.get("medicalHistory", "None"),  # Not required - default value
        implantHistory=form_data.get("implantHistory", "None"),  # Not required - default value
        medications=form_data.get("medications", "None"),  # Not required - default value
        dataConsent=form_data.get("dataConsent", False),  # Not required - default value
        installationConsent=form_data.get("installationConsent", False),  # Not required - default value
        marketingConsent=form_data.get("marketingConsent", False),  # Not required - default value
        additionalRequirements=form_data.get("additionalRequirements", "None"),  # Not required - default value
    )

    print(order_data)

    #file_path = f"{order_data.name.replace(' ', '_')}_order.pdf"
    file_path = "order_details.pdf"
    generate_pdf(order_data, file_path)
    
    return FileResponse(path=file_path, filename=file_path, media_type="application/pdf")

def _generate_form(json: Any) -> str:
    html = Element("html", {"lang": "pl"})
    tree = ElementTree(html)
    head = ET.SubElement(html, "head")

    meta_charset = ET.SubElement(head, "meta", {"charset": "UTF-8"})

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

    form.append(Element("input", {"type": "button", "onclick": "downloadPDF()", "value": "Pobierz PDF", "style": "display: inline-block; margin-left: 10px;"}))

    script = ET.SubElement(body, "script")
    script.text = """
    function downloadPDF() {
        const form = document.querySelector('form');
        const formData = new FormData(form);
        const queryString = new URLSearchParams(formData).toString();
        window.location.href = `/download?${queryString}`;
    }
    """

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


# TODO: Implement the PDF generation logic here using some library
def generate_pdf(data: OrderData, file_path: str):

    data_dict = data.dict()
    # Dummy PDF
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R >>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Length 55 >>\n"
        b"stream\n"
        b"BT\n"
        b"/F1 24 Tf\n"
        b"100 100 Td\n"
        b"(Hello, PDF World!) Tj\n"
        b"ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000056 00000 n \n"
        b"0000000103 00000 n \n"
        b"0000000191 00000 n \n"
        b"trailer\n"
        b"<< /Root 1 0 R /Size 5 >>\n"
        b"startxref\n"
        b"263\n"
        b"%%EOF"
    )

    # Step 1: Load the existing PDF
    input_pdf = PdfReader("original.pdf")
    output_pdf = PdfWriter()

    # Step 2: Loop through each page and fill form fields
    for page in input_pdf.pages:
        # Access form fields
        if "/Annots" in page:
            for annotation in page["/Annots"]:
                field = annotation.get_object()
                # Check if the field name is in the dictionary and fill it
                field_name = field.get

    with open(file_path, "wb") as f:
        f.write(pdf_content)

# This is needed for debugging.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
