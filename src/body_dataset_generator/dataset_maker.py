from download_data import download_raw_body_dataset
from hard_negative_df_generator import build_hard_negative_rows
import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "body_dataset.csv"

def build_body_dataset():
    hard_negative_df = build_hard_negative_rows()
    raw_body_df = download_raw_body_dataset()
    combined_df = pd.concat([hard_negative_df, raw_body_df], ignore_index=True)
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

    final_df = combined_df[["text", "label", "category"]]
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"benign rows: {len(hard_negative_df)}")
    print(f"malicious rows: {len(raw_body_df)}")
    print(f"combined (after dedup): {len(final_df)}")
    print(f"label distribution:\n{final_df['label'].value_counts()}")
    print(f"Saved to {OUTPUT_PATH}")

    return final_df

if __name__ == "__main__":
    combined_df_final = build_body_dataset()
