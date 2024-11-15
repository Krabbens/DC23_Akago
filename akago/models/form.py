from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, Literal, Optional, TypeAlias

from pydantic import BaseModel, computed_field


class FormFieldPosition(BaseModel):
    page: int
    x0: float
    y0: float
    x1: float
    y1: float


class BaseFormField(BaseModel, ABC):
    position: FormFieldPosition


class BaseFormFieldGroup(BaseModel, ABC):
    @property
    @abstractmethod
    def subfields(self) -> Iterable[BaseFormField]: ...

    @computed_field
    @property
    def position(self) -> FormFieldPosition:
        page: Optional[int] = None
        x0: Optional[float] = None
        y0: Optional[float] = None
        x1: Optional[float] = None
        y1: Optional[float] = None

        for subfield in self.subfields:
            if page is None or subfield.position.page < page:
                page = subfield.position.page

            if x0 is None or subfield.position.x0 < x0:
                x0 = subfield.position.x0

            if y0 is None or subfield.position.y0 < y0:
                y0 = subfield.position.y0

            if x1 is None or subfield.position.x1 > x1:
                x1 = subfield.position.x1

            if y1 is None or subfield.position.y1 > y1:
                y1 = subfield.position.y1

        return FormFieldPosition(
            page=page or 0, x0=x0 or 0, y0=y0 or 0, x1=x1 or 0, y1=y1 or 0
        )


class FormInputType(str, Enum):
    BLOOD = "blood"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    TEXT = "text"


class FormInput(BaseFormField):
    type: Literal["input"] = "input"
    input_type: FormInputType


class FormRadio(BaseFormField):
    type: Literal["radio"] = "radio"
    value: str


class FormRadioGroup(BaseFormFieldGroup):
    type: Literal["radioGroup"] = "radioGroup"
    radios: list[FormRadio]

    @property
    def subfields(self) -> Iterable[BaseFormField]:
        return self.radios


class FormTableCell(BaseFormField):
    type: Literal["tableCell"] = "tableCell"
    row_index: int
    col_name: str


class FormTable(BaseFormFieldGroup):
    type: Literal["table"] = "table"
    cells: list[FormTableCell]

    @property
    def subfields(self) -> Iterable[BaseFormField]:
        return self.cells


FormField: TypeAlias = FormInput | FormRadioGroup | FormTable


class FormMetadata(BaseModel):
    fields: dict[str, FormField] = {}
