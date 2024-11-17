import json
import sys
from pathlib import Path
import fitz
from pdf_analyzer.analyze import PDFAnalyzer
from pdf_analyzer.transform import DataTransformer
from pdf_analyzer.validate import DynamicModelCreator

DATA_DIR = Path("data")
FORM_PATH = Path(DATA_DIR / "AkagoFormFilled.pdf")
METADATA_PATH = Path(DATA_DIR / "form_metadata.json")
EXTRACTED_DATA_PATH = Path(DATA_DIR / "form_data.json")

metadata: dict

# Wczytanie metadanych
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
data_transformer = DataTransformer(metadata)
model_creator = DynamicModelCreator(metadata)
data = analyzer.analyze_pdf(pdf)

transformed_data = data_transformer.transform_data(data)

try:
    validated_data = model_creator.validate(transformed_data)
except Exception as e:
    print(f"Validation failed: {e}", file=sys.stderr)
    sys.exit(1)

EXTRACTED_DATA_PATH.write_text(
    json.dumps(validated_data.model_dump_json(), indent=4, ensure_ascii=False, allow_nan=False),
    encoding="utf-8",
)

print("Data extraction, transformation, and validation completed successfully.")
