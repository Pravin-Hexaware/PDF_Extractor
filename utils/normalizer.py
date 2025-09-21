import os
import json
import re
from difflib import get_close_matches
from utils.logger import _write_log

# Resolve absolute path to header_map.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "header_map.json")
CONFIG_PATH = os.path.abspath(CONFIG_PATH)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    HEADER_MAP = json.load(f)

SENTINEL = "__MISSING__"

def normalize_header(header):
    """
    Maps raw header to canonical metric name using HEADER_MAP.
    Falls back to fuzzy match or UNMAPPED:: prefix.
    """
    if not isinstance(header, str):
        header = str(header)

    header = header.strip()
    if header in HEADER_MAP:
        return HEADER_MAP[header]

    matches = get_close_matches(header, HEADER_MAP.keys(), n=1, cutoff=0.8)
    if matches:
        return HEADER_MAP[matches[0]]

    _write_log(f"UNMAPPED HEADER: {header}")
    return f"UNMAPPED::{header}"

def parse_number(value):
    """
    Parses a numeric string into float.
    Handles currency, commas, and negative values in parentheses.
    Returns SENTINEL if parsing fails.
    """
    if not value or not isinstance(value, str):
        return SENTINEL

    value = value.strip().replace(",", "").replace("$", "")
    value = re.sub(r"\((.*?)\)", r"-\1", value)

    try:
        return float(value)
    except ValueError:
        _write_log(f"MALFORMED VALUE: {value}")
        return SENTINEL

def normalize_table(dataframes, org_name):
    """
    Converts raw DataFrames into a normalized metric dict.
    Uses HEADER_MAP and fuzzy matching to align keys.
    """
    normalized = {}

    for df in dataframes:
        for _, row in df.iterrows():
            for col, val in row.items():
                norm_key = normalize_header(str(col))
                norm_val = parse_number(str(val))
                if norm_key not in normalized or normalized[norm_key] == SENTINEL:
                    normalized[norm_key] = norm_val

    return normalized