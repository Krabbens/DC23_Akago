import json
import sys
from pathlib import Path

import fitz

from pdf_analyzer.analyze import PDFAnalyzer

DATA_DIR = Path("data")
FORM_PATH = Path(DATA_DIR / "AkagoForm.pdf")
METADATA_PATH = Path(DATA_DIR / "form_metadata.json")
EXTRACTED_DATA_PATH = Path(DATA_DIR / "form_data.json")

metadata: dict

try:
    metadata = METADATA_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    print(
        "Form metadata isn't generated. Run the extract_form_metadata script first",
        file=sys.stderr,
    )
    sys.exit(1)

metadata = json.loads(metadata)
pdf = fitz.open(FORM_PATH)
analyzer = PDFAnalyzer(metadata)
data = analyzer.analyze_pdf(pdf)

EXTRACTED_DATA_PATH.write_text(
    json.dumps(data, indent=4, ensure_ascii=False, allow_nan=False),
    encoding="utf-8",
)
