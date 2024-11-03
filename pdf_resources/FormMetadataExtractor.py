import fitz  # PyMuPDF
import json
import re
import os

class FormMetadataExtractor:
    @staticmethod
    def extract(input_pdf_path, output_json_path=None):
        """
        Extracts form metadata from a PDF and saves it as a JSON file.
        
        Parameters:
        - input_pdf_path (str): The path to the input PDF file.
        - output_json_path (str, optional): The path to save the output JSON file. 
          If not provided, the output file name will be generated based on the input file name.

        Returns:
        - str: The path to the saved JSON file.
        """
        # Open the PDF document
        doc = fitz.open(input_pdf_path)
        form_metadata = {
            "fields": [],
            "checkbox_groups": {},
            "lists": {}
        }

        # Regular expressions to match lists, checkboxes, and standard form fields
        list_pattern = re.compile(r"(.+?)_(\d+)_(.+)")
        checkbox_pattern = re.compile(r"cb_(.+?)_(.+)")

        # Iterate through each page of the document
        for page_num in range(len(doc)):
            page = doc[page_num]
            fields = page.widgets()  # Get all form fields on the current page

            for field in fields:
                field_name = field.field_name
                field_rect = field.rect  # Field position as a rectangle

                # Check if the field is a checkbox
                checkbox_match = checkbox_pattern.match(field_name)
                if checkbox_match:
                    group_name = checkbox_match.group(1)
                    item_name = checkbox_match.group(2)

                    # Initialize the checkbox group if it doesn't exist
                    if group_name not in form_metadata["checkbox_groups"]:
                        form_metadata["checkbox_groups"][group_name] = []

                    # Add checkbox data to the group
                    form_metadata["checkbox_groups"][group_name].append({
                        "name": item_name,
                        "page": page_num,
                        "rect": {
                            "x1": field_rect.x0,
                            "y1": field_rect.y0,
                            "x2": field_rect.x1,
                            "y2": field_rect.y1
                        }
                    })

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
                    form_metadata["lists"][list_name].append({
                        "index": list_index,
                        "name": item_name,
                        "page": page_num,
                        "rect": {
                            "x1": field_rect.x0,
                            "y1": field_rect.y0,
                            "x2": field_rect.x1,
                            "y2": field_rect.y1
                        }
                    })

                # If the field is a standard text field
                else:
                    form_metadata["fields"].append({
                        "type": "text_field",
                        "name": field_name,
                        "page": page_num,
                        "rect": {
                            "x1": field_rect.x0,
                            "y1": field_rect.y0,
                            "x2": field_rect.x1,
                            "y2": field_rect.y1
                        }
                    })

        # Generate default output path if not provided
        if not output_json_path:
            output_json_path = os.path.splitext(input_pdf_path)[0] + "_metadata.json"

        # Save metadata to a JSON file
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(form_metadata, f, indent=4, ensure_ascii=False)

        print(f"Form metadata saved to: {output_json_path}")
        return output_json_path