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
    form_metadata = []

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

                # Add radio data directly to the form metadata
                form_metadata.append(
                    {
                        "type": "radio",
                        "name": group_name,
                        "value": item_name,
                        "position": {
                            "page": page_num,
                            "x0": field_rect.x0,
                            "y0": field_rect.y0,
                            "x1": field_rect.x1,
                            "y1": field_rect.y1,
                        },
                    }
                )

            # Check if the field is part of a list
            elif list_pattern.match(field_name):
                list_match = list_pattern.match(field_name)
                list_name = list_match.group(1)
                list_index = int(list_match.group(2))
                item_name = list_match.group(3)

                # Check for '%' in item_name to extract type
                if "%" in item_name:
                    col_name, field_type = item_name.split("%", 1)
                else:
                    col_name = item_name
                    field_type = "text"

                # Add list item data as tablecell
                form_metadata.append(
                    {
                        "type": "tablecell",
                        "name": list_name,
                        "row": list_index,
                        "col": col_name,
                        "input_type": field_type.strip(),
                        "position": {
                            "page": page_num,
                            "x0": field_rect.x0,
                            "y0": field_rect.y0,
                            "x1": field_rect.x1,
                            "y1": field_rect.y1,
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

                form_metadata.append(
                    {
                        "type": "input",
                        "name": field_name,
                        "input_type": field_type,
                        "position": {
                            "page": page_num,
                            "x0": field_rect.x0,
                            "y0": field_rect.y0,
                            "x1": field_rect.x1,
                            "y1": field_rect.y1,
                        },
                    }
                )

    return {"fields": form_metadata}
