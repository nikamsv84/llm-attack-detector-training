from src.header_dataset_gen.header_df_generator import BENIGN_HEADER_PATH, MALICIOUS_HEADER_PATH, build_benign_header_rows, build_malicious_header_rows
from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "header_dataset.csv"


def build_header_dataset() -> pd.DataFrame:
    benign_df = build_benign_header_rows()
    malicious_df = build_malicious_header_rows()

    combined_df = pd.concat([benign_df, malicious_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["field_name", "text"])
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    combined_df["category"] = combined_df["category"].fillna("benign")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(OUTPUT_PATH, index=False)

    return combined_df


if __name__ == "__main__":
    combined_df = build_header_dataset()
    print(combined_df["label"].value_counts())
    print(combined_df["category"].value_counts())
