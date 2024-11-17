from pydantic import BaseModel, create_model, EmailStr, field_validator
from typing import Dict, Any, Type, Optional
from datetime import date
import re

class DynamicModelCreator:
    def __init__(self, metadata: Dict[str, Any]):
        type_map = {
            "text": str,
            "email": EmailStr,
            "date": date,
            "radio": Dict[str, bool]
        }

        fields = {}
        for field in metadata["fields"]:
            ft = field.get("type", "")
            field_type = type_map.get(ft, None)

            if field_type is None:
                input_type = field.get("input_type", "text")
                field_type = type_map.get(input_type, str)

            if ft == "tablecell":
                #optional
                fields[field["name"]] = (Optional[field_type], None)
            else:
                #required
                fields[field["name"]] = (Optional[field_type], ...)    

        self.model: Type[BaseModel] = create_model('DynamicModel', **fields)
        print(self.model.__annotations__)

    def validate(self, data: Dict[str, Any]) -> BaseModel:
        return self.model(**data)

    def transform_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.strftime('%Y-%m-%d')
        return data
