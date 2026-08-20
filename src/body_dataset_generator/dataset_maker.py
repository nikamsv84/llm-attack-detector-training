from pathlib import Path
import pandas as pd

from src.body_dataset_generator.download_data import download_raw_body_dataset
from src.body_dataset_generator.hard_negative_df_generator import build_hard_negative_rows
from src.body_dataset_generator.download_general_benign_data import download_general_benign_samples

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "body_dataset.csv"


def build_body_dataset() -> pd.DataFrame:
    hard_negative_df = build_hard_negative_rows()
    raw_body_df = download_raw_body_dataset()
    general_benign_df = download_general_benign_samples()

    combined_df = pd.concat(
        [hard_negative_df, raw_body_df, general_benign_df],
        ignore_index=True,
    )
    combined_df = combined_df.drop_duplicates(subset=["text"])
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

    final_df = combined_df[["text", "label", "category"]]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"hard negative rows: {len(hard_negative_df)}")
    print(f"raw body rows: {len(raw_body_df)}")
    print(f"general benign rows: {len(general_benign_df)}")
    print(f"combined (after dedup): {len(final_df)}")
    print(f"label distribution:\n{final_df['label'].value_counts()}")
    print(f"Saved to {OUTPUT_PATH}")

    return final_df


if __name__ == "__main__":
    build_body_dataset()