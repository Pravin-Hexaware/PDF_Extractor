# run.py

import argparse
import os
from pipelines.run_pipeline import run_comparison_pipeline

def validate_inputs(pdf_paths):
    for path in pdf_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        if not path.lower().endswith(".pdf"):
            raise ValueError(f"Invalid file type (expected PDF): {path}")

def main():
    parser = argparse.ArgumentParser(description="Compare financial tables across organizations.")
    parser.add_argument("pdfs", nargs=2, help="Paths to two financial PDF documents")
    parser.add_argument("--output", default="data/output.json", help="Path to save comparison JSON")
    parser.add_argument("--html", action="store_true", help="Also export extracted tables to HTML")

    args = parser.parse_args()
    validate_inputs(args.pdfs)

    org_a_path, org_b_path = args.pdfs
    output_path = args.output

    print(f"🔍 Starting comparison between:\n  - {org_a_path}\n  - {org_b_path}")
    run_comparison_pipeline(
        pdf_paths=[org_a_path, org_b_path],
        output_json=output_path,
        export_html=args.html
    )
    print(f"✅ Comparison complete. Output saved to: {output_path}")

if __name__ == "__main__":
    main()