import pymupdf

from akago.config import FORM_METADATA_PATH, FORM_PATH
from akago.pdf.metadata import extract_metadata

print("Generating form metadata...")

doc = pymupdf.open(FORM_PATH)
metadata = extract_metadata(doc)

FORM_METADATA_PATH.write_text(metadata.model_dump_json(indent=4), encoding="utf-8")
