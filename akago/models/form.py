from enum import Enum
from typing import Literal, Self, TypeAlias

from pydantic import BaseModel

from akago.models.metadata import FieldMetadata, InputType, Metadata


class FormInputType(str, Enum):
    DATE = "date"
    EMAIL = "email"
    TEL = "tel"
    TEXT = "text"


class FormInput(BaseModel):
    type: Literal["input"] = "input"
    input_type: FormInputType
    label: str


class FormRadio(BaseModel):
    label: str
    value: str


class FormRadioGroup(BaseModel):
    type: Literal["radiogroup"] = "radiogroup"
    label: str
    radios: list[FormRadio]


class FormTableColumn(BaseModel):
    label: str
    name: str


class FormTable(BaseModel):
    type: Literal["table"] = "table"
    label: str
    row_count: int
    columns: list[FormTableColumn]

class FormPickListItem(BaseModel):
    value: str
    is_extra: bool

class FormPickList(BaseModel):
    type: Literal["picklist"] = "picklist"
    label: str
    options: list[FormPickListItem]

FormField: TypeAlias = FormInput | FormRadioGroup | FormTable | FormPickList


class Form(BaseModel):
    fields: dict[str, FormField] = {}

    @classmethod
    def from_metadata(cls, metadata: Metadata) -> Self:
        form = cls()

        for field_metadata in sorted(metadata.fields, key=_get_position_key):
            name = field_metadata.name

            match field_metadata.type:
                case "input":
                    if name in form.fields:
                        raise ValueError(
                            f"Field name '{name}' is given to two separate input fields"
                        )

                    form.fields[name] = FormInput(
                        input_type=_get_form_input_type(field_metadata.input_type),
                        label=_get_form_field_label(name),
                    )
                case "radio":
                    value = field_metadata.value
                    radio_group = form.fields.setdefault(
                        name,
                        FormRadioGroup(label=_get_form_field_label(name), radios=[]),
                    )

                    if not isinstance(radio_group, FormRadioGroup):
                        raise ValueError(
                            f"Field name '{name}' is duplicated between two incompatible form field types: '{radio_group.type}' and 'radio'"
                        )

                    radio_group.radios.append(
                        FormRadio(
                            label=_get_form_field_label(value),
                            value=value,
                        )
                    )
                case "tablecell":
                    row = field_metadata.row
                    col = field_metadata.col
                    table = form.fields.setdefault(
                        name,
                        FormTable(
                            label=_get_form_field_label(name), row_count=0, columns=[]
                        ),
                    )

                    if not isinstance(table, FormTable):
                        raise ValueError(
                            f"Field name '{name}' is duplicated between two incompatible form field types: '{table.type}' and 'table'"
                        )

                    if not any(col == column.name for column in table.columns):
                        table.columns.append(
                            FormTableColumn(label=_get_form_field_label(col), name=col)
                        )

                    if row > table.row_count:
                        table.row_count = row
                case "picklist":
                    picklist = form.fields.setdefault(
                        name,
                        FormPickList(
                            label=_get_form_field_label(name), options=[]
                        ),
                    )

                    if not isinstance(picklist, FormPickList):
                        raise ValueError(
                            f"Field name '{name}' is duplicated between two incompatible form field types: '{picklist.type}' and 'picklist'"
                        )

                    picklist_items = next(
                        (item for item in _PICKLIST_OPTIONS if item["name"] == name),
                        None,
                    )

                    if picklist_items is None:
                        raise ValueError(f"No picklist items found for field '{name}'")
                    
                    picklist.options = [
                        FormPickListItem(
                            value=item["value"], is_extra=item["is_extra"]
                        )
                        for item in picklist_items["options"]
                    ]


        return form


def _get_position_key(field_metadata: FieldMetadata) -> tuple[int, float, float]:
    return (
        field_metadata.position.page,
        field_metadata.position.y0,
        field_metadata.position.x0,
    )


def _get_form_input_type(input_type: InputType) -> FormInputType:
    match input_type:
        case InputType.BLOOD | InputType.TEXT:
            return FormInputType.TEXT
        case InputType.DATE:
            return FormInputType.DATE
        case InputType.EMAIL:
            return FormInputType.EMAIL
        case InputType.PHONE:
            return FormInputType.TEL


_LABELS = {
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

_PICKLIST_OPTIONS = [
    {
        "name": "implantType",
        "options": [
            {"value": "Bioniczna Ręka", "is_extra": False},
            {"value": "Syntetyczne Płuca", "is_extra": False},
            {"value": "Cyber Oko", "is_extra": False},
            {"value": "Syntetyczne Serce", "is_extra": False},
            {"value": "Syntetyczna Skóra", "is_extra": False},
            {"value": "Mechaniczne Płuca", "is_extra": False},
            {"value": "Syntetyczna Ręka", "is_extra": False},
            {"value": "Mechaniczne Nogi", "is_extra": False},
            {"value": "Syntetyczny Kręgosłup", "is_extra": True},
            {"value": "Syntetyczna Czaszka", "is_extra": True}
        ]
    }
]


def _get_form_field_label(name: str) -> str:
    return _LABELS[name]
