import os
import shutil
import tempfile

from extractors.camelot_extractor import extract_tables_camelot
from extractors.pdfplumber_extractor import extract_tables_pdfplumber
from extractors.ocr_extractor import extract_tables_ocr
from utils.normalizer import normalize_table
from validators.health_check import validate_metrics
from utils.logger import log_skipped, log_unmapped, log_extraction_failure
from utils.file_utils import save_html, save_json

def run_comparison_pipeline(pdf_paths, output_json, export_html=False):
    results = []

    for pdf_path in pdf_paths:
        org_name = os.path.splitext(os.path.basename(pdf_path))[0]
        print(f"\n📄 Processing: {org_name}")

        tables = None
        temp_dir = tempfile.mkdtemp()

        try:
            # Step 1: Try Camelot extraction
            try:
                tables = extract_tables_camelot(pdf_path)
            except Exception as e:
                print(f"❌ Camelot extraction failed for {pdf_path}: {e}")
                log_extraction_failure(pdf_path, "Camelot", str(e))

            if not tables:
                print("⚠️ Camelot failed. Trying pdfplumber...")
                try:
                    tables = extract_tables_pdfplumber(pdf_path)
                except Exception as e:
                    print(f"❌ pdfplumber extraction failed for {pdf_path}: {e}")
                    log_extraction_failure(pdf_path, "pdfplumber", str(e))

            if not tables:
                print("⚠️ pdfplumber failed. Trying OCR fallback...")
                try:
                    tables = extract_tables_ocr(pdf_path, temp_dir=temp_dir)
                except Exception as e:
                    print(f"❌ OCR extraction failed for {pdf_path}: {e}")
                    log_extraction_failure(pdf_path, "OCR", str(e))

            if not tables:
                print(f"❌ No tables extracted from {pdf_path}. Skipping.")
                log_skipped(org_name, reason="No extractable tables")
                continue

            # Step 2: Normalize tables
            normalized_metrics = normalize_table(tables, org_name)

            # Step 3: Validate required metrics
            validated_metrics = validate_metrics(normalized_metrics, org_name)

            # Step 4: Log unmapped headers or missing fields
            log_unmapped(validated_metrics, org_name)

            # Step 5: Save HTML (optional)
            if export_html:
                html_path = f"data/{org_name}.html"
                save_html(tables, html_path)
                print(f"🧾 HTML saved to: {html_path}")

            # Step 6: Append to results
            results.append({
                "organization": org_name,
                "metrics": validated_metrics
            })

        finally:
            # Step 7: Clean up temp directory safely
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"⚠️ Could not delete temp dir {temp_dir}: {e}")
                log_extraction_failure(temp_dir, "TempCleanup", str(e))

    # Step 8: Save final comparison JSON
    save_json(results, output_json)
    print(f"\n📊 Final comparison saved to: {output_json}")