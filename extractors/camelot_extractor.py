import camelot
import pandas as pd
import re
from utils.logger import log_extraction_failure, _write_log

def extract_tables_camelot(pdf_path, max_pages=30):
    """
    Extracts tables from a multi-page PDF using Camelot.
    Tries both lattice and stream per page, selects best result.
    Preserves horizontal and vertical headers.
    Returns a list of cleaned pandas DataFrames.
    """

    def extract_best_mode(pdf_path, page_num):
        best_tables = []
        best_mode = None
        best_score = 0

        for flavor in ["lattice", "stream"]:
            try:
                tables = camelot.read_pdf(
                    pdf_path,
                    flavor=flavor,
                    pages=str(page_num),
                    strip_text='\n'
                )
                if tables and tables.n > 0:
                    score = sum(t.df.shape[0] * t.df.shape[1] for t in tables)
                    if score > best_score:
                        best_tables = tables
                        best_mode = flavor
                        best_score = score
            except Exception as e:
                log_extraction_failure(pdf_path, f"Camelot-{flavor}", f"Page {page_num} → {e}")
        return best_tables, best_mode

    def split_compound_rows(df):
        new_rows = []
        for _, row in df.iterrows():
            label = str(row.iloc[0])
            values = row.iloc[1:].tolist()
            segments = re.split(r'(?<=[a-z])(?=[A-Z])|(?<=:)\s+|(?<=\))\s+', label)
            segments = [seg.strip() for seg in segments if seg.strip()]
            if len(segments) == len(values):
                for seg, val in zip(segments, values):
                    new_rows.append([seg] + [val])
            else:
                new_rows.append([label] + values)
        return pd.DataFrame(new_rows, columns=["Metric"] + df.columns[1:].tolist())

    def clean_tables(tables, mode, page_num):
        cleaned = []
        for i, table in enumerate(tables):
            df = table.df
            df = df.dropna(how='all').replace('', pd.NA).dropna(how='all', axis=1)
            if df.empty or df.shape[1] == 0:
                continue

            # Merge multi-line headers
            if df.shape[0] > 2:
                h1 = df.iloc[0].fillna("")
                h2 = df.iloc[1].fillna("")
                df.columns = [f"{a} {b}".strip() for a, b in zip(h1, h2)]
                df = df[2:]
            elif df.shape[0] > 1:
                df.columns = df.iloc[0]
                df = df[1:]

            # Promote first column as vertical label
            if df.shape[1] > 1:
                df.rename(columns={df.columns[0]: "Metric"}, inplace=True)

            # Split compound metric rows
            df = split_compound_rows(df)
            cleaned.append(df.reset_index(drop=True))

        if cleaned:
            _write_log(f"EXTRACTION MODE: {pdf_path} → Page {page_num} → {mode}")
        return cleaned

    all_cleaned = []
    for page_num in range(1, max_pages + 1):
        tables, mode = extract_best_mode(pdf_path, page_num)
        if tables:
            cleaned = clean_tables(tables, mode, page_num)
            all_cleaned.extend(cleaned)

    return all_cleaned