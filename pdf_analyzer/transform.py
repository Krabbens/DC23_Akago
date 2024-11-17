import re
from datetime import datetime
import morfeusz2


class DataTransformer:
    """
    A class to transform data based on its type.

    Attributes:
    - type_map (dict): A mapping of data types to transformation functions.
    - morfeusz (Morfeusz): An instance of the Morfeusz2 library for Polish language analysis.
    """

    def __init__(self, metadata):
        """
        Initializes the DataTransformer class with predefined types and transformation functions.
        """
        self.metadata = metadata
        self.type_map = {
            "text": self.transform_text,  # Handles basic text transformation
            "date": self.transform_date,  # Handles date transformation
            "phone": self.transform_phone  # Handles phone number normalization
        }
        self.morfeusz = morfeusz2.Morfeusz()

    def transform_data(self, data: dir)-> dir:
        transformed_data = {}
        for field, value in data.items():
            field_metadata = next((f for f in self.metadata["fields"] if f["name"] == field), None)
            if field_metadata:
                field_type = field_metadata.get("input_type", "text")
                transformed_data[field] = self.transform(field_type, value)
            else:
                transformed_data[field] = value
        return transformed_data

    def transform(self, type_name: str, value: str) -> str:
        """
        Transforms the input value based on its type.

        Parameters:
        - type_name (str): The name of the data type.
        - value (str): The value to transform.

        Returns:
        - str: The transformed value.
        """
        if type_name in self.type_map:
            return self.type_map[type_name](value)
        else:
            return value

    def transform_text(self, value: str) -> str:
        return value

    def transform_date(self, value: str) -> str:
        # Common date formats
        base_date_formats = [
            '%d/%m/%Y', '%Y/%m/%d', '%d.%m.%Y', '%Y.%m.%d',
            '%d-%m-%Y', '%Y-%m-%d', '%d %m %Y', '%Y %m %d',
            '%d %B %Y', '%d %b %Y'  # Formats with month names
        ]

        # Replace all separators with spaces for uniform parsing
        normalized_value = re.sub(r'[-./]', ' ', value)

        for date_format in base_date_formats:
            try:
                parsed_date = datetime.strptime(normalized_value, date_format)
                return parsed_date.strftime('%Y-%m-%d')  # Return in standard format
            except ValueError:
                continue  # Try the next format

        # Handle dates with Polish month names
        try:
            day, month_word, year = normalized_value.split()
            month = self.get_month(month_word)
            if month != -1:
                parsed_date = datetime(int(year), month, int(day))
                return parsed_date.strftime('%Y-%m-%d')
        except (ValueError, IndexError):
            pass

        raise ValueError(
            "Invalid date format. Expected formats include dd/mm/yyyy, yyyy.mm.dd, etc."
        )

    def transform_phone(self, value: str) -> str:
        return ''.join(c for c in value if c.isdigit() or c == '+')

    def get_month(self, word: str) -> int:
        months = [
            "styczeń", "luty", "marzec", "kwiecień", "maj",
            "czerwiec", "lipiec", "sierpień", "wrzesień",
            "październik", "listopad", "grudzień"
        ]
        try:
            basic = self.morfeusz.analyse(word.lower())[0][2][1]  # Normalize to basic form
            return months.index(basic) + 1
        except (IndexError, ValueError):
            return -1