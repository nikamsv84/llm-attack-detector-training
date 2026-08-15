import json
from pathlib import Path
import pandas as pd

BENIGN_HEADER_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "header_raw_datasets" / "benign_headers_source.json"
MALICIOUS_HEADER_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "header_raw_datasets" / "malicious_header_conflicts.json"


def build_benign_header_rows():
    """benign_headers_source.json schema: [{"headers": {field: value, ...}}, ...]"""
    with open(BENIGN_HEADER_PATH) as f:
        entries = json.load(f)

    seen = set()
    rows = []
    for entry in entries:
        headers = entry.get("headers", {})
        key = tuple(sorted(headers.items()))
        if key in seen:
            continue
        seen.add(key)
        for field_name, value in headers.items():
            rows.append({
                "source_field": "header",
                "field_name": field_name,
                "text": value,
                "label": False,
            })

    return pd.DataFrame(rows).drop_duplicates(subset=["field_name", "text"])


def build_malicious_header_rows():
    """malicious_header_conflicts.json schema: [{"header_field_name", "header_value", "body_snippet", "label"}, ...]"""
    with open(MALICIOUS_HEADER_PATH) as f:
        entries = json.load(f)

    rows = []
    for entry in entries:
        rows.append({
            "source_field": "header",
            "field_name": entry["header_field_name"],
            "text": entry["header_value"],
            "label": True,
            "category":entry.get("label") # e.g. "model_override", keep for analysis
        })

    return pd.DataFrame(rows).drop_duplicates(subset=["field_name", "text"])


if __name__ == "__main__":
    benign_df = build_benign_header_rows()
    malicious_df = build_malicious_header_rows()
    print(f"benign rows: {len(benign_df)}")
    print(f"malicious rows: {len(malicious_df)}")
    print(malicious_df.head(10))