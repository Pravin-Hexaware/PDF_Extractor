# validators/health_check.py

REQUIRED_METRICS = [
    "Revenue",
    "Net Income",
    "Current Ratio",
    "Debt/Equity",
    "Cash Flow"
]

SENTINEL = "__MISSING__"

def validate_metrics(metrics_dict, org_name):
    """
    Ensures all required metrics are present.
    Inserts sentinel values for missing fields.
    Logs missing fields for auditability.
    """
    validated = {}
    missing_fields = []

    for key in REQUIRED_METRICS:
        if key in metrics_dict and metrics_dict[key] != SENTINEL:
            validated[key] = metrics_dict[key]
        else:
            validated[key] = SENTINEL
            missing_fields.append(key)

    if missing_fields:
        print(f"⚠️ {org_name}: Missing metrics → {', '.join(missing_fields)}")

    # Preserve any extra metrics that were extracted
    for key, val in metrics_dict.items():
        if key not in validated:
            validated[key] = val

    return validated