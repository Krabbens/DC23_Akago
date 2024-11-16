from enum import Enum
from typing import Literal, TypeAlias

from pydantic import BaseModel


class FieldPosition(BaseModel):
    page: int
    x0: float
    y0: float
    x1: float
    y1: float


class InputType(str, Enum):
    BLOOD = "blood"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    TEXT = "text"


class InputMetadata(BaseModel):
    type: Literal["input"] = "input"
    name: str
    input_type: InputType
    position: FieldPosition


class RadioMetadata(BaseModel):
    type: Literal["radio"] = "radio"
    name: str
    value: str
    position: FieldPosition


class TableCellMetadata(BaseModel):
    type: Literal["tablecell"] = "tablecell"
    name: str
    row: int
    col: str
    position: FieldPosition


FieldMetadata: TypeAlias = InputMetadata | RadioMetadata | TableCellMetadata


class Metadata(BaseModel):
    fields: list[FieldMetadata] = []
