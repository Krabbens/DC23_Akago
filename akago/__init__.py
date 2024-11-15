from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from akago.config import FORM_METADATA_PATH
from akago.models.form import FormFieldPosition, FormMetadata
from akago.templates import templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root(request: Request) -> HTMLResponse:
    metadata_json = FORM_METADATA_PATH.read_text(encoding="utf-8")
    metadata = FormMetadata.model_validate_json(metadata_json, strict=True)
    fields: list[dict] = []
    labels: dict[str, str] = {
        "fullname": "Imię i nazwisko",
        "address": "Adres",
        "phoneNumber": "Telefon",
        "email": "Adres e-mail",
        "birthDate": "Data urodzenia",
        "sex": "Płeć",
        "male": "Mężczyzna",
        "female": "Kobieta",
        "other": "Inna",
        "idNumber": "Numer identyfikacyjny",
        "implantType": "Rodzaj augmentacji",
        "implantPurpose": "Cel augmentacji",
        "estheticPreferences": "Osobiste preferencje estetyczne",
        "additonalFeatures": "Dodatkowe opcje",
        "feature": "Opcja",
        "installationDate": "Data instalacji",
        "preferredFacility": "Preferowana placówka",
        "additionalRequirements": "Dodatkowe wymagania",
        "requirement": "Wymaganie",
        "bloodGroup": "Grupa krwi",
        "medicalHistory": "Historia chorób",
        "disease": "Choroba",
        "diagnosisDate": "Data rozpoznania",
        "treatment": "Leczenie",
        "currentStatus": "Aktualny status",
        "implantHistory": "Historia augmentacji",
        "type": "Rodzaj augmentacji",
        "producer": "Producent",
        "serialNumber": "Numer seryjny",
        "medications": "Lista aktualnie przyjmowanych leków",
        "name": "Nazwa leku",
        "dose": "Dawka",
        "frequency": "Częstotliwość",
        "comment": "Uwagi",
        "personalDataConsent": "Zgoda na przetwarzanie danych osobowych",
        "intallationConsent": "Zgoda na przeprowadzenie instalacji wszczepu",
        "yes": "Tak",
        "no": "Nie",
    }

    for name, field in sorted(
        metadata.fields.items(), key=lambda item: _get_position_key(item[1].position)
    ):
        match field.type:
            case "radioGroup":
                field.radios = sorted(
                    field.radios,
                    key=lambda radio: _get_position_key(radio.position),
                )
            case "table":
                field.cells = sorted(
                    field.cells, key=lambda cell: _get_position_key(cell.position)
                )
            case _:
                pass

        serialized_field = field.model_dump(
            mode="json",
            exclude={
                "position": True,
                "radios": {"__all__": {"position"}},
                "cells": {"__all__": {"position"}},
            },
        )

        fields.append({**serialized_field, "name": name})

    return templates.TemplateResponse(
        request, "form.jinja", context={"fields": fields, "labels": labels}
    )


def _get_position_key(position: FormFieldPosition) -> tuple[int, float, float]:
    return (position.page, position.y0, position.x0)
