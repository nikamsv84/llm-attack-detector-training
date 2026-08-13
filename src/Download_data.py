from datasets import load_dataset, concatenate_datasets
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "neuralchemy_core.csv"

def download_and_save():
    print("Downloading dataset from HuggingFace...")
    ds = load_dataset("neuralchemy/Prompt-injection-dataset", "core")
    all_data = concatenate_datasets([ds["train"], ds["validation"], ds["test"]])
    df = all_data.to_pandas()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")

if __name__ == "__main__":
    download_and_save()