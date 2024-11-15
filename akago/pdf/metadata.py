import re
from typing import Iterable, Optional, TypedDict, cast

from pymupdf import Document, Page, Rect, Widget

from akago.models.form import (
    FormFieldPosition,
    FormInput,
    FormInputType,
    FormMetadata,
    FormRadio,
    FormRadioGroup,
    FormTable,
    FormTableCell,
)

_TABLE_PATTERN = re.compile(r"(.+?)_(\d+)_(.+)")
_RADIO_PATTERN = re.compile(r"rb_(.+?)_(.+)")


class _InputData(TypedDict):
    name: str
    input_type: FormInputType


class _RadioData(TypedDict):
    name: str
    value: str


class _TableData(TypedDict):
    name: str
    row_index: int
    col_name: str


def extract_metadata(doc: Document) -> FormMetadata:
    inputs: dict[str, FormInput] = {}
    radio_groups: dict[str, FormRadioGroup] = {}
    tables: dict[str, FormTable] = {}
    pages: Iterable[Page] = doc.pages()

    for page in pages:
        widgets: Iterable[Widget] = page.widgets()

        for widget in widgets:
            field_name = cast(str, widget.field_name)
            field_rect = cast(Rect, widget.rect)

            position = FormFieldPosition(
                page=cast(int, page.number),
                x0=field_rect.x0,
                y0=field_rect.y0,
                x1=field_rect.x1,
                y1=field_rect.y1,
            )
            data = _parse_radio_data(field_name)

            if data is not None:
                radio = FormRadio(value=data["value"], position=position)

                if data["name"] in radio_groups:
                    radio_groups[data["name"]].radios.append(radio)
                else:
                    radio_groups[data["name"]] = FormRadioGroup(radios=[radio])

                continue

            data = _parse_table_data(field_name)

            if data is not None:
                cell = FormTableCell(
                    row_index=data["row_index"],
                    col_name=data["col_name"],
                    position=position,
                )

                if data["name"] in tables:
                    tables[data["name"]].cells.append(cell)
                else:
                    tables[data["name"]] = FormTable(cells=[cell])

                continue

            data = _parse_input_data(field_name)
            input = FormInput(input_type=data["input_type"], position=position)
            inputs[data["name"]] = input

    return FormMetadata(fields=inputs | radio_groups | tables)


def _parse_input_data(field_name: str) -> _InputData:
    if "%" in field_name:
        name, input_type = field_name.split("%", maxsplit=1)

        try:
            input_type = FormInputType(input_type)
        except ValueError:
            raise ValueError(f"Unsupported input type '{input_type}'")

        return {"name": name.strip(), "input_type": input_type}
    else:
        return {"name": field_name.strip(), "input_type": FormInputType.TEXT}


def _parse_radio_data(field_name: str) -> Optional[_RadioData]:
    result = _RADIO_PATTERN.match(field_name)

    if result is not None:
        name = result.group(1)
        value = result.group(2)

        return {"name": name, "value": value}

    return None


def _parse_table_data(field_name: str) -> Optional[_TableData]:
    result = _TABLE_PATTERN.match(field_name)

    if result is not None:
        name = result.group(1)
        row_index = int(result.group(2))
        col_name = result.group(3)

        return {"name": name, "row_index": row_index, "col_name": col_name}

    return None
