import re
from typing import Iterable, Optional, TypedDict, cast

import pymupdf
from pymupdf import Document, Page, Rect, Widget

from akago.config import FORM_METADATA_PATH, FORM_PATH
from akago.models.metadata import (
    FieldPosition,
    InputMetadata,
    InputType,
    Metadata,
    RadioMetadata,
    TableCellMetadata,
)

_TABLE_PATTERN = re.compile(r"(.+?)_(\d+)_(.+)")
_RADIO_PATTERN = re.compile(r"rb_(.+?)_(.+)")


class _InputData(TypedDict):
    name: str
    input_type: InputType


class _RadioData(TypedDict):
    name: str
    value: str


class _TableData(TypedDict):
    name: str
    row_index: int
    col_name: str


def get_metadata() -> Metadata:
    try:
        metadata_json = FORM_METADATA_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return create_metadata()

    return Metadata.model_validate_json(metadata_json, strict=True)


def create_metadata() -> Metadata:
    doc = pymupdf.open(FORM_PATH)
    metadata = extract_metadata(doc)

    FORM_METADATA_PATH.write_text(metadata.model_dump_json(indent=4), encoding="utf-8")

    return metadata


def extract_metadata(doc: Document) -> Metadata:
    metadata = Metadata()
    pages: Iterable[Page] = doc.pages()

    for page in pages:
        widgets: Iterable[Widget] = page.widgets()

        for widget in widgets:
            field_name = cast(str, widget.field_name)
            field_rect = cast(Rect, widget.rect)

            position = FieldPosition(
                page=cast(int, page.number),
                x0=field_rect.x0,
                y0=field_rect.y0,
                x1=field_rect.x1,
                y1=field_rect.y1,
            )
            data = _parse_radio_data(field_name)

            if data is not None:
                metadata.fields.append(
                    RadioMetadata(
                        name=data["name"], value=data["value"], position=position
                    )
                )

                continue

            data = _parse_table_data(field_name)

            if data is not None:
                metadata.fields.append(
                    TableCellMetadata(
                        name=data["name"],
                        row=data["row_index"],
                        col=data["col_name"],
                        position=position,
                    )
                )

                continue

            data = _parse_input_data(field_name)
            metadata.fields.append(
                InputMetadata(
                    name=data["name"], input_type=data["input_type"], position=position
                )
            )

    return metadata


def _parse_input_data(field_name: str) -> _InputData:
    if "%" in field_name:
        name, input_type = field_name.split("%", maxsplit=1)

        try:
            input_type = InputType(input_type)
        except ValueError:
            raise ValueError(f"Unsupported input type '{input_type}'")

        return {"name": name.strip(), "input_type": input_type}
    else:
        return {"name": field_name.strip(), "input_type": InputType.TEXT}


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
