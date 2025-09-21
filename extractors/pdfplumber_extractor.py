import pdfplumber
import pandas as pd
from utils.logger import log_extraction_failure

def extract_tables_pdfplumber(pdf_path, max_pages=5):
    """
    Extracts tables from a text-based PDF using pdfplumber.
    Returns a list of cleaned pandas DataFrames.
    """
    extracted_tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages[:max_pages], start=1):
                tables = page.extract_tables()
                if not tables:
                    continue

                for raw_table in tables:
                    df = pd.DataFrame(raw_table)

                    # Drop empty rows and columns
                    df = df.dropna(how='all').replace('', pd.NA).dropna(how='all', axis=1)

                    # Defensive check: skip malformed tables
                    if df.empty or df.shape[1] == 0:
                        continue

                    # Promote first row to header if it looks like column names
                    if df.shape[0] > 1 and all(isinstance(x, str) for x in df.iloc[0]):
                        df.columns = df.iloc[0]
                        df = df[1:]

                    extracted_tables.append(df.reset_index(drop=True))

        return extracted_tables

    except Exception as e:
        print(f"❌ pdfplumber extraction failed for {pdf_path}: {e}")
        log_extraction_failure(pdf_path, "pdfplumber", str(e))
        return []