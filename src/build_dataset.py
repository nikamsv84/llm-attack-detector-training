import pandas as pd
from pathlib import Path
from src.dataset_gen.hard_negative import HARD_NEGATIVES_MANUAL

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

KEEP_COLUMNS = ["text", "label"]

def load_neuralchemy():
    df = pd.read_csv(RAW_DIR / "neuralchemy_core.csv")
    return df[KEEP_COLUMNS]

def load_manual_hard_negatives():
    df = pd.DataFrame(HARD_NEGATIVES_MANUAL)
    df["label"] = 0
    return df[KEEP_COLUMNS]
def build_dataset():
    neuralchemy_df = load_neuralchemy()
    manual_df = load_manual_hard_negatives()

    combined_df = pd.concat([neuralchemy_df, manual_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset="text")
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "training_dataset.csv"
    combined_df.to_csv(output_path, index=False)

    print(f"neuralchemy rows: {len(neuralchemy_df)}")
    print(f"manual hard negatives: {len(manual_df)}")
    print(f"combined (after dedup): {len(combined_df)}")
    print(f"label distribution:\n{combined_df['label'].value_counts()}")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    build_dataset()