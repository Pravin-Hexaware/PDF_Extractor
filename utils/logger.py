import os
from datetime import datetime

LOG_FILE = "data/audit_log.txt"

def _write_log(message):
    """
    Writes a message to the log file with timestamp.
    Ensures UTF-8 encoding and safe directory creation.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.abspath(LOG_FILE)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"⚠️ Failed to write to log: {e}")

def log_skipped(org_name, reason):
    """
    Logs when a document or table is skipped.
    """
    msg = f"SKIPPED: {org_name} → Reason: {reason}"
    print(f"⚠️ {msg}")
    _write_log(msg)

def log_unmapped(metrics_dict, org_name):
    """
    Logs any headers that were not mapped to the normalized schema.
    """
    unmapped = [k for k in metrics_dict.keys() if k.startswith("UNMAPPED::")]
    if unmapped:
        msg = f"UNMAPPED HEADERS in {org_name}: {', '.join(unmapped)}"
        print(f"🧩 {msg}")
        _write_log(msg)

def log_extraction_failure(pdf_path, extractor_name, error):
    """
    Logs extraction failures with traceback info.
    """
    msg = f"EXTRACTION FAILED: {pdf_path} via {extractor_name} → {error}"
    print(f"❌ {msg}")
    _write_log(msg)