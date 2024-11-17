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

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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

    file_path = "order_details.pdf"
    generate_pdf(order_data, file_path)
    
    return FileResponse(path=file_path, filename=file_path, media_type="application/pdf")

@app.get("/logo.png")
def get_logo():
    return FileResponse("public/logo.png")

@app.get("/form", response_class=HTMLResponse)
def _generate_form() -> str:
    def html(content):  # Also allows you to set your own <head></head> etc
        return '<html><head><link rel="stylesheet" href="https://unpkg.com/sakura.css/css/sakura-dark.css" type="text/css"></head><body>' + content + '</body></html>'
    with open("pdf_resources/AkagoForm_metadata.json", "r") as f:
        data = json.load(f)

    translations = {
        "fullname": "Pełne imię", "address": "Adres", "phone": "Telefon", "email": "Email",
        "birthDate": "Data urodzenia", "idNumber": "Numer ID", "implantType": "Typ implantu",
        "implantPurpose": "Cel implantu", "estheticPreferences": "Preferencje estetyczne",
        "installationDate": "Data instalacji", "preferredFacility": "Preferowane miejsce",
        "bloodGroup": "Grupa krwi", "gender": "Płeć", "personalDataConsent": "Zgoda na przetwarzanie danych osobowych",
        "intallationConsent": "Zgoda na instalację", "additonalFeatures": "Dodatkowe funkcje",
        "additionalRequirements": "Dodatkowe wymagania", "medicalHistory": "Historia medyczna",
        "implantHistory": "Historia implantów", "medications": "Leki", "disease": "Choroba",
        "diagnosisDate": "Data diagnozy", "treatment": "Leczenie", "currentStatus": "Obecny status",
        "type": "Typ", "producer": "Producent", "serialNumber": "Numer seryjny",
        "name": "Nazwa", "dose": "Dawka", "frequency": "Częstotliwość", "comment": "Komentarz",
        "feature": "Funkcja", "requirement": "Wymaganie"
    }

    all_data = []
    for field in data["fields"]:
        all_data.append({"name": field["name"], "type": "field", "x": field["rect"]["x1"], "y": field["rect"]["y1"], "p": field["page"]})
    for group_name, checkboxes in data["checkbox_groups"].items():
        sorted_checkboxes = sorted(checkboxes, key=lambda x: (x["page"], x["rect"]["y1"], x["rect"]["x1"]))
        all_data.append({"group_name": group_name, "checkboxes": sorted_checkboxes, "type": "checkbox", "x": sorted_checkboxes[0]["rect"]["x1"], "y": sorted_checkboxes[0]["rect"]["y1"], "p": sorted_checkboxes[0]["page"]})
    for list_name, items in data["lists"].items():
        sorted_items = sorted(items, key=lambda x: (x["page"], x["rect"]["y1"], x["rect"]["x1"]))
        all_data.append({"list_name": list_name, "items": sorted_items, "type": "list", "x": sorted_items[0]["rect"]["x1"], "y": sorted_items[0]["rect"]["y1"], "p": sorted_items[0]["page"]})

    all_data = sorted(all_data, key=lambda x: (x["p"], x["y"], x["x"]))
    
    html_form = '<body style="text-align: center;"><form method="POST">'

    # add image
    html_form += '<img src="logo.png" style="width: 64px; height: 64px;">'

    # Sort and process fields
    for element in all_data:
        if element["type"] == "field":
            field_name = element["name"]
            field_label = translations.get(field_name, field_name.capitalize())
            html_form += f'<label for="{field_name}">{field_label}:</label>'
            html_form += f'<input type="text" id="{field_name}" name="{field_name}"><br>'

        # Sort and process checkbox groups
        if element["type"] == "checkbox":
            group_label = translations.get(element["group_name"], element["group_name"])
            html_form += f'<fieldset><legend>{group_label}</legend>'
            
            for checkbox in element["checkboxes"]:
                checkbox_name = checkbox["name"]
                checkbox_label = translations.get(checkbox_name, checkbox_name.capitalize())
                html_form += f'<label for="{checkbox_name}">{checkbox_label}'
                html_form += f'<input type="checkbox" id="{checkbox_name}" name="{group_name}[]" value="{checkbox_name}"></label>'
            
            html_form += '</fieldset><br>\n'

        # Sort and process lists
        if element["type"] == "list":
            list_label = translations.get(element["list_name"], element["list_name"])
            html_form += f'<strong>{list_label}</strong>'
            html_form += '<table><tr>'

            # Remove duplicates in items based on `name`
            unique_items = []
            for item in element["items"]:
                if item["name"] not in [unique["name"] for unique in unique_items]:
                    unique_items.append(item)
            
            for item in unique_items:
                item_label = translations.get(item["name"], item["name"].capitalize())
                html_form += f'<th>{item_label}</th>'
            
            html_form += '</tr>\n'

            # Create rows for input fields
            m = 3
            for _ in range(m):
                html_form += '<tr>'
                for item in unique_items:
                    item_name = item["name"]
                    html_form += f'<td><input type="text" name="{list_name}_{item_name}[]"></td>'
                html_form += '</tr>'

            html_form += '</table><br>'

    html_form += '</form>'

    script_for_pdf = """
     function downloadPDF() {
        const form = document.querySelector('form');
        const formData = new FormData(form);
        const queryString = new URLSearchParams(formData).toString();
        window.location.href = `/download?${queryString}`;
    }
    """

    html_form += f'<script>{script_for_pdf}</script>'

    html_form += f'<button type="submit">Submit</button>'
    html_form += f'<br>'
    html_form += f'<button onclick="downloadPDF()">Download PDF</button>'
    html_form += '</body>'

    return html(html_form)

def generate_pdf(data: OrderData, file_path: str):
    # Register the font that supports Polish characters
    pdfmetrics.registerFont(TTFont('DejaVu', 'public/DejaVuSans.ttf'))
    # Create a SimpleDocTemplate
    pdf = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    
    # Define styles
    # Define styles using the registered font
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='TitleStyle', fontSize=16, leading=20, alignment=1, fontName='DejaVu', spaceAfter=20)
    normal_style = ParagraphStyle(name='NormalStyle', fontSize=12, fontName='DejaVu')
    bold_style = ParagraphStyle(name='BoldStyle', fontSize=12, fontName='DejaVu', leading=14, spaceAfter=6)
    
    # Adding the logo
    logo_path = 'public/logo.png'
    try:
        logo = Image(logo_path, width=1.2 * inch, height=1.2 * inch)
        elements.append(logo)
    except FileNotFoundError:
        elements.append(Paragraph("Logo not found", normal_style))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Title
    elements.append(Paragraph("Wniosek o Personalizowaną Augmentację Cybernetyczną", title_style))
    
    # Section: Personal Information
    elements.append(Paragraph("Dane Personalne Klienta", bold_style))
    personal_info = [
        ['Imię i nazwisko:', data.name],
        ['Adres zamieszkania:', data.address],
        ['Numer telefonu:', data.phoneEmail],
        ['Data urodzenia:', data.birthDate],
        ['Płeć:', data.gender],
        ['Numer identyfikacyjny:', data.idNumber],
    ]
    
    personal_table = Table(personal_info, colWidths=[2.5 * inch, 3.5 * inch])
    personal_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(personal_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Section: Augmentation Details
    elements.append(Paragraph("Dane Dotyczące Augmentacji", bold_style))
    augmentation_info = [
        ['Rodzaj augmentacji:', data.implantType],
        ['Cel augmentacji:', data.implantPurpose],
        ['Osobiste preferencje estetyczne:', data.estheticPreferences],
        ['Termin instalacji:', data.installationDate],
        ['Preferowana placówka:', data.preferredFacility],
    ]
    
    augmentation_table = Table(augmentation_info, colWidths=[2.5 * inch, 3.5 * inch])
    augmentation_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(augmentation_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Section: Medical Information
    elements.append(Paragraph("Informacje Medyczne", bold_style))
    medical_info = [
        ['Grupa krwi:', data.bloodGroup],
        ['RH:', data.rh],
        ['Historia chorób:', data.medicalHistory],
        ['Historia Augmentacji:', data.implantHistory],
        ['Aktualne leki:', data.medications],
    ]
    
    medical_table = Table(medical_info, colWidths=[2.5 * inch, 3.5 * inch])
    medical_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(medical_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Section: Consents
    elements.append(Paragraph("Zgody i oświadczenia", bold_style))
    consents = [
        ['Zgoda na przetwarzanie danych osobowych:', "Tak" if data.dataConsent else "Nie"],
        ['Zgoda na instalację wszczepu:', "Tak" if data.installationConsent else "Nie"],
        ['Zgoda na marketing:', "Tak" if data.marketingConsent else "Nie"],
    ]
    
    consent_table = Table(consents, colWidths=[3.5 * inch, 1.5 * inch])
    consent_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(consent_table)

    # Build the PDF
    pdf.build(elements)



# This is needed for debugging.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
