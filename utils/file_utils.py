from pathlib import Path
import html
import json
import pandas as pd
from utils.logger import _write_log

STYLE = """
<style>
body { font-family: Arial, sans-serif; padding: 20px; }
table.financial-table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
table.financial-table th, table.financial-table td {
    border: 1px solid #ccc; padding: 8px; text-align: left;
}
table.financial-table th { background-color: #f2f2f2; }
</style>
"""

def log_output(path, kind):
    _write_log(f"OUTPUT SAVED: {kind} → {path}")

def save_html(dataframes, output_path):
    """
    Saves a list of pandas DataFrames as a single HTML file.
    Each table is wrapped in <div> for separation.
    """
    html_parts = []
    for i, df in enumerate(dataframes):
        html_parts.append(f"<h3>Table {i+1}</h3>")
        html_parts.append(df.to_html(index=False, border=1, classes="financial-table"))

    full_html = f"<html><head>{STYLE}</head><body>" + "\n".join(html_parts) + "</body></html>"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    log_output(str(output_path), "HTML")

def save_tables_as_html(tables, out_dir: str):
    """
    Saves each table (dict with 'header', 'rows', 'page') as a separate HTML file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, tbl in enumerate(tables):
        fname = out_dir / f"table_p{tbl['page']}_{i}.html"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"<html><head>{STYLE}</head><body><table class='financial-table'>\n")

            if tbl.get("header"):
                f.write("<thead><tr>")
                for h in tbl["header"]:
                    f.write(f"<th>{html.escape(str(h))}</th>")
                f.write("</tr></thead>\n")

            f.write("<tbody>")
            for row in tbl.get("rows", []):
                f.write("<tr>")
                for cell in row:
                    f.write(f"<td>{html.escape(str(cell))}</td>")
                f.write("</tr>\n")
            f.write("</tbody></table></body></html>")

        log_output(str(fname), "HTML Table")

def save_json(data, output_path):
    """
    Saves a Python dict or list to a JSON file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    log_output(str(output_path), "JSON")

def save_markdown(dataframes, output_path):
    """
    Saves a list of DataFrames as Markdown tables.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for i, df in enumerate(dataframes):
            f.write(f"### Table {i+1}\n")
            f.write(df.to_markdown(index=False))
            f.write("\n\n")

    log_output(str(output_path), "Markdown")

def save_csv(dataframes, out_dir):
    """
    Saves each DataFrame as a separate CSV file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, df in enumerate(dataframes):
        csv_path = out_dir / f"table_{i+1}.csv"
        df.to_csv(csv_path, index=False)
        log_output(str(csv_path), "CSV")