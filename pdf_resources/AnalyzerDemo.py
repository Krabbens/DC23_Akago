import os
from PDFAnalyzer import PDFAnalyzer
from FormMetadataExtractor import FormMetadataExtractor

def main():
    pdf_meta_path = "AkagoForm.pdf"  # Input PDF file
    metadata_output_path = None   # Metadata will be saved with default name

    # Extract form metadata from the PDF and save to a JSON file
    metadata_json_path = FormMetadataExtractor.extract(pdf_meta_path, metadata_output_path)
    print(f"Form metadata extracted and saved to: {metadata_json_path}")

    # Analyze the PDF using the extracted metadata
    analyzer = PDFAnalyzer(metadata_json_path)
    pdf_path = "data\\lena.pdf"
    results_json_path = analyzer.analyze_pdf(pdf_path)
    print(f"Analysis results saved to: {results_json_path}")


if __name__ == "__main__":
    main()