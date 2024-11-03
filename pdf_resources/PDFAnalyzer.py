import fitz  # PyMuPDF
import json
import os
from collections import defaultdict

class PDFAnalyzer:
    def __init__(self, metadata_path):
        """
        Initializes the PDFAnalyzer with the path to the metadata file.

        Parameters:
        - metadata_path (str): Path to the JSON metadata file that describes the form structure.
        """
        self.metadata_path = metadata_path
        self.metadata = self._load_metadata()

    def analyze_pdf(self, pdf_path, output_path=None):
        """
        Analyzes a PDF document and extracts form data based on the loaded metadata.

        Parameters:
        - pdf_path (str): Path to the input PDF file.
        - output_path (str or None): Path to save the output JSON file. If None, a default path is created.

        Returns:
        - dict: Extracted form data.
        """
        self.doc = fitz.open(pdf_path)
        self.results = defaultdict(lambda: defaultdict(dict))

        self._analyze_fields()
        self._analyze_radioes()
        self._analyze_lists()

        # Determine output path if not provided
        if output_path is None:
            base_path, _ = os.path.splitext(pdf_path)
            output_path = f"{base_path}_processed.json"

        # Save the results to a JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dict(self.results), f, ensure_ascii=False, indent=4)

        return output_path

    def _load_metadata(self):
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _word_in_rect(self, word_rect, field_rect, tolerance=0.5):
        field_fitz_rect = fitz.Rect(
            field_rect["x1"] - tolerance,
            field_rect["y1"] - tolerance,
            field_rect["x2"] + tolerance,
            field_rect["y2"] + tolerance
        )
        return word_rect.intersects(field_fitz_rect) or (
            word_rect.x0 >= field_fitz_rect.x0 and
            word_rect.y0 >= field_fitz_rect.y0 and
            word_rect.x1 <= field_fitz_rect.x1 and
            word_rect.y1 <= field_fitz_rect.y1
        )

    def _analyze_fields(self):
        for field in self.metadata["fields"]:
            field_name = field["name"]
            page_num = field["page"]
            field_rect = field["rect"]
            page = self.doc[page_num]
            field_result = []

            for word in page.get_text("words"):
                word_rect = fitz.Rect(word[:4])
                if self._word_in_rect(word_rect, field_rect):
                    field_result.append(word[4])

            if field_result:
                self.results[field_name] = " ".join(field_result)

    def _analyze_radioes(self):
        for group_name, radioes in self.metadata["radio_groups"].items():
            group_result = {}
            for radio in radioes:
                page_num = radio["page"]
                field_rect = radio["rect"]
                page = self.doc[page_num]
                radio_name = radio["name"]

                radio_checked = any(
                    self._word_in_rect(fitz.Rect(word[:4]), field_rect)
                    for word in page.get_text("words")
                )
                group_result[radio_name] = radio_checked
            self.results[group_name] = group_result

    def _analyze_lists(self):
        for list_name, items in self.metadata["lists"].items():
            max_index = max(item["index"] for item in items)
            list_results = [{} for _ in range(max_index + 1)]

            for item in items:
                page_num = item["page"]
                page = self.doc[page_num]
                item_rect = item["rect"]
                item_index = item["index"]
                item_name = item["name"]
                field_result = []

                for word in page.get_text("words"):
                    word_rect = fitz.Rect(word[:4])
                    if self._word_in_rect(word_rect, item_rect):
                        field_result.append(word[4])

                if field_result:
                    list_results[item_index][item_name] = " ".join(field_result)

            self.results[list_name] = [item for item in list_results if item]
