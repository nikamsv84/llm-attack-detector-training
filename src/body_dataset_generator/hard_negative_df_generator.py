import json
from pathlib import Path
import pandas as pd

HARD_NEGATIVE_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "body_raw_datasets" / "hard_negatives_manual.json"


def build_hard_negative_rows() -> pd.DataFrame:

    with open(HARD_NEGATIVE_PATH) as f:
        entries = json.load(f)

    rows = []
    for entry in entries:
        rows.append({
            "text": entry["text"],
            "label": 0,
            "tags": entry.get("tags", []),
            "category":"benign"
        })

    return pd.DataFrame(rows).drop_duplicates(subset=["text"])


if __name__ == "__main__":
    hard_negative_df = build_hard_negative_rows()
    print(f"hard negative rows: {len(hard_negative_df)}")
    print(hard_negative_df.head(10))