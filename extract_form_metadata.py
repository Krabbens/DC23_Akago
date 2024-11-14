import json
from pathlib import Path

import fitz

from pdf_analyzer.extract import extract_metadata

DATA_DIR = Path("data")
FORM_PATH = Path(DATA_DIR / "AkagoForm.pdf")
METADATA_PATH = Path(DATA_DIR / "form_metadata.json")

pdf = fitz.open(FORM_PATH)
metadata = extract_metadata(pdf)

METADATA_PATH.write_text(
    json.dumps(metadata, indent=4, ensure_ascii=False, allow_nan=False),
    encoding="utf-8",
)
