# type: ignore -- pymupdf has very poor typing support.
import mimetypes

from pymupdf import Document, Page

from akago.models.request import AugmentationRequest


def create_document(request: AugmentationRequest) -> Document:
    doc = Document(filetype=mimetypes.types_map[".pdf"], fontsize=12)
    page: Page = doc.new_page()

    # TODO: Generate an actual PDF document. See https://pymupdf.readthedocs.io/en/latest/page.html
    # for documentation.
    page.insert_text((12, 12), "Hello world")

    return doc
