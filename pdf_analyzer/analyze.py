from collections import defaultdict
from fitz import Document, Rect

class PDFAnalyzer:
    def __init__(self, metadata: dict):
        """
        Initializes the PDFAnalyzer with the metadata.
        """
        self.metadata = metadata

    def analyze_pdf(self, pdf: Document) -> dict:
        """
        Analyzes a PDF document and extracts form data based on the loaded metadata.

        Parameters:
        - pdf (Document): The PDF file.

        Returns:
        - dict: Extracted form data.
        """
        self.pdf = pdf
        self.results = {}

        self._analyze_fields()

        return self.results

    def _word_in_rect(self, word_rect, field_rect, tolerance=0.5):
        field_fitz_rect = Rect(
            field_rect["x0"] - tolerance,
            field_rect["y0"] - tolerance,
            field_rect["x1"] + tolerance,
            field_rect["y1"] + tolerance,
        )
        return word_rect.intersects(field_fitz_rect) or (
            word_rect.x0 >= field_fitz_rect.x0
            and word_rect.y0 >= field_fitz_rect.y0
            and word_rect.x1 <= field_fitz_rect.x1
            and word_rect.y1 <= field_fitz_rect.y1
        )

    def _analyze_fields(self):
        for field in self.metadata["fields"]:
            field_type = field["type"]
            field_name = field["name"]
            page_num = field["position"]["page"]
            field_rect = field["position"]
            page = self.pdf[page_num]
            field_result = []

            if field_type == "input" or field_type == "tablecell":
                # Handle text input and tablecell types
                for word in page.get_text("words"):
                    word_rect = Rect(word[:4])
                    if self._word_in_rect(word_rect, field_rect):
                        field_result.append(word[4])

                if field_result:
                    self.results[field_name] = " ".join(field_result)

            elif field_type == "radio":
                # Handle radio button types (grouped by name)
                radio_value = field["value"]
                radio_checked = any(
                    self._word_in_rect(Rect(word[:4]), field_rect)
                    for word in page.get_text("words")
                )
                if field_name not in self.results:
                        self.results[field_name] = {}
                if radio_checked:
                    self.results[field_name][radio_value] = True
                else:
                    self.results[field_name][radio_value] = False

            elif field_type == "checkbox":
                # Handle checkboxes (yes/no fields, for example)
                checkbox_value = field["value"]
                checkbox_checked = any(
                    self._word_in_rect(Rect(word[:4]), field_rect)
                    for word in page.get_text("words")
                )

                if checkbox_checked:
                    if field_name not in self.results:
                        self.results[field_name] = {
                            "yes": False,
                            "no": False
                        }
                    self.results[field_name][checkbox_value] = True

            elif field_type == "tablecell":
                # Handle list-like structures (like `additonalFeatures`)
                field_result.append(self._extract_table_data(page, field_rect, field_name))
                if field_result:
                    self.results.setdefault(field_name, []).append({
                        field["col"]: " ".join(field_result)
                    })

    def _extract_table_data(self, page, rect, field_name):
        table_data = []
        for word in page.get_text("words"):
            word_rect = Rect(word[:4])
            if self._word_in_rect(word_rect, rect):
                table_data.append(word[4])
        return table_data