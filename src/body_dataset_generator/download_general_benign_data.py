from datasets import load_dataset
import pandas as pd


def download_general_benign_samples(sample_size: int = 5000) -> pd.DataFrame:
    print("Downloading GooAQ dataset from HuggingFace (streaming mode)...")
    ds = load_dataset("sentence-transformers/gooaq", "pair", split="train", streaming=True)

    rows = []
    for i, example in enumerate(ds):
        if i >= sample_size:
            break
        rows.append({
            "text": example["question"],
            "label": 0,
            "category": "benign",
            "source": "gooaq_general",
        })

    result_df = pd.DataFrame(rows).drop_duplicates(subset=["text"])
    print(f"Downloaded {len(result_df)} general benign samples.")
    return result_df


if __name__ == "__main__":
    df = download_general_benign_samples()
    print(df.head(10))