import camelot
import pandas as pd
from utils.logger import log_extraction_failure

def extract_tables_camelot(pdf_path, max_pages=5):
    """
    Extracts tables from a vector-based PDF using Camelot.
    Tries lattice mode first, then falls back to stream mode.
    Returns a list of cleaned pandas DataFrames.
    """
    def clean_tables(tables):
        cleaned = []
        for i, table in enumerate(tables):
            df = table.df
            df = df.dropna(how='all').replace('', pd.NA).dropna(how='all', axis=1)
            if df.empty or df.shape[1] == 0:
                continue
            if df.shape[0] > 1 and all(isinstance(x, str) for x in df.iloc[0]):
                df.columns = df.iloc[0]
                df = df[1:]
            cleaned.append(df.reset_index(drop=True))
        return cleaned

    try:
        tables = camelot.read_pdf(
            pdf_path,
            flavor='lattice',
            pages=f'1-{max_pages}',
            strip_text='\n'
        )
        cleaned = clean_tables(tables)
        if cleaned:
            return cleaned
        else:
            print(f"⚠️ Lattice mode found no usable tables. Trying stream mode...")
            tables_stream = camelot.read_pdf(
                pdf_path,
                flavor='stream',
                pages=f'1-{max_pages}',
                strip_text='\n'
            )
            return clean_tables(tables_stream)

    except Exception as e:
        print(f"❌ Camelot extraction failed for {pdf_path}: {e}")
        log_extraction_failure(pdf_path, "Camelot", str(e))
        return []