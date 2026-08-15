from datasets import load_dataset, concatenate_datasets
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "body_raw_datasets"/"neuralchemy_core.csv"

def download_raw_body_dataset():
    print("Downloading dataset from HuggingFace...")
    ds = load_dataset("neuralchemy/Prompt-injection-dataset", "core")
    all_data = concatenate_datasets([ds["train"], ds["validation"], ds["test"]])
    df = all_data.to_pandas()

    return df


if __name__ == "__main__":
    df = download_raw_body_dataset()
