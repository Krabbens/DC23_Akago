import re

from fitz import Document


def extract_metadata(pdf: Document) -> dict:
    """
    Extracts form metadata from a PDF and saves it as a JSON file.

    Parameters:
    - pdf (Document): The PDF file.

    Returns:
    - dict: JSON representing the form metadata.
    """
    form_metadata = {"fields": [], "radio_groups": {}, "lists": {}}

    # Regular expressions to match lists and radios
    list_pattern = re.compile(r"(.+?)_(\d+)_(.+)")
    radio_pattern = re.compile(r"rb_(.+?)_(.+)")

    # Iterate through each page of the document
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        fields = page.widgets()  # Get all form fields on the current page

        for field in fields:
            field_name = field.field_name
            field_rect = field.rect  # Field position as a rectangle

            # Check if the field is a radio
            radio_match = radio_pattern.match(field_name)
            if radio_match:
                group_name = radio_match.group(1)
                item_name = radio_match.group(2)

                # Initialize the radio group if it doesn't exist
                if group_name not in form_metadata["radio_groups"]:
                    form_metadata["radio_groups"][group_name] = []

                # Add radio data to the group
                form_metadata["radio_groups"][group_name].append(
                    {
                        "name": item_name,
                        "page": page_num,
                        "rect": {
                            "x1": field_rect.x0,
                            "y1": field_rect.y0,
                            "x2": field_rect.x1,
                            "y2": field_rect.y1,
                        },
                    }
                )

            # Check if the field is part of a list
            elif list_pattern.match(field_name):
                list_match = list_pattern.match(field_name)
                list_name = list_match.group(1)
                list_index = int(list_match.group(2))
                item_name = list_match.group(3)

                # Initialize the list if it doesn't exist
                if list_name not in form_metadata["lists"]:
                    form_metadata["lists"][list_name] = []

                # Add list item data
                form_metadata["lists"][list_name].append(
                    {
                        "index": list_index,
                        "name": item_name,
                        "page": page_num,
                        "rect": {
                            "x1": field_rect.x0,
                            "y1": field_rect.y0,
                            "x2": field_rect.x1,
                            "y2": field_rect.y1,
                        },
                    }
                )

            # If the field is a standard text field
            else:
                # Determine the field type based on the presence of '%'
                if "%" in field_name:
                    name_part, type_part = field_name.split("%", 1)
                    field_type = type_part.strip()  # Extract and trim the type
                    field_name = name_part.strip()  # Update field_name without type
                else:
                    field_type = "text"  # Default type if not specified

                form_metadata["fields"].append(
                    {
                        "type": field_type,
                        "name": field_name,
                        "page": page_num,
                        "rect": {
                            "x1": field_rect.x0,
                            "y1": field_rect.y0,
                            "x2": field_rect.x1,
                            "y2": field_rect.y1,
                        },
                    }
                )

    return form_metadata
