from collections import defaultdict

from fitz import Document, Rect


class PDFAnalyzer:
    def __init__(self, metadata: dict):
        """
        Initializes the PDFAnalyzer with the path to the metadata file.

        Parameters:
        - metadata_path (str): Path to the JSON metadata file that describes the form structure.
        """
        self.metadata = metadata

    def analyze_pdf(self, pdf: Document) -> dict:
        """
        Analyzes a PDF document and extracts form data based on the loaded metadata.

        Parameters:
        - pdf (str): The PDF file.

        Returns:
        - dict: Extracted form data.
        """
        self.pdf = pdf
        self.results = defaultdict(lambda: defaultdict(dict))

        self._analyze_fields()
        self._analyze_radio_groups()
        self._analyze_lists()

        return self.results

    def _word_in_rect(self, word_rect, field_rect, tolerance=0.5):
        field_fitz_rect = Rect(
            field_rect["x1"] - tolerance,
            field_rect["y1"] - tolerance,
            field_rect["x2"] + tolerance,
            field_rect["y2"] + tolerance,
        )
        return word_rect.intersects(field_fitz_rect) or (
            word_rect.x0 >= field_fitz_rect.x0
            and word_rect.y0 >= field_fitz_rect.y0
            and word_rect.x1 <= field_fitz_rect.x1
            and word_rect.y1 <= field_fitz_rect.y1
        )

    def _analyze_fields(self):
        for field in self.metadata["fields"]:
            field_name = field["name"]
            page_num = field["page"]
            field_rect = field["rect"]
            page = self.pdf[page_num]
            field_result = []

            for word in page.get_text("words"):
                word_rect = Rect(word[:4])
                if self._word_in_rect(word_rect, field_rect):
                    field_result.append(word[4])

            if field_result:
                self.results[field_name] = " ".join(field_result)

    def _analyze_radio_groups(self):
        for group_name, radios in self.metadata["radio_groups"].items():
            group_result = {}
            for radio in radios:
                page_num = radio["page"]
                field_rect = radio["rect"]
                page = self.pdf[page_num]
                radio_name = radio["name"]

                radio_checked = any(
                    self._word_in_rect(Rect(word[:4]), field_rect)
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
                page = self.pdf[page_num]
                item_rect = item["rect"]
                item_index = item["index"]
                item_name = item["name"]
                field_result = []

                for word in page.get_text("words"):
                    word_rect = Rect(word[:4])
                    if self._word_in_rect(word_rect, item_rect):
                        field_result.append(word[4])

                if field_result:
                    list_results[item_index][item_name] = " ".join(field_result)

            self.results[list_name] = [item for item in list_results if item]
