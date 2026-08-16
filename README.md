# LLM Attack Detector — Training Pipeline

This repository builds and trains two lightweight machine learning classifiers used by [LLM Inspector](#), a MITM security proxy for LLM API traffic. The models classify incoming requests as **benign** or **malicious**, replacing (or augmenting) simple pattern-matching detection with something that generalizes better to variations of known attack patterns.

Two independent models are trained here:

- **Header model** — flags malicious HTTP headers (e.g. attempts to override the target model, disable safety filters, or escalate privileges via custom headers).
- **Body model** — flags malicious request bodies (e.g. prompt injection, jailbreak attempts, instruction override).

Each model is trained, evaluated, and exported separately, then loaded independently inside the proxy's `analyzer.py`.

## Why two separate models?

Header values and request bodies have very different structure. A header value like `gpt-4-unrestricted` is a short, ungrammatical string — there's no sentence structure to exploit. A request body is a full sentence with grammar and context. Because of this, each model uses a different text vectorization strategy (see [Approach](#approach) below), so it made sense to keep the two pipelines — and the two trained models — fully independent.

## Project structure

```
data/
  raw/
    header_raw_datasets/
      benign_headers_source.json       # manually collected benign headers (from real proxy traffic)
      malicious_header_conflicts.json  # manually authored malicious header samples
    body_raw_datasets/
      neuralchemy_core.csv             # downloaded from HuggingFace (neuralchemy/Prompt-injection-dataset)
      hard_negatives_manual.json       # manually authored benign samples that resemble attacks (false-positive guards)
  processed/
    header_dataset.csv                 # combined, deduplicated header dataset
    body_dataset.csv                   # combined, deduplicated body dataset
src/
  header_dataset_gen/
    header_df_generator.py             # loads raw header JSON -> DataFrame
    dataset_maker.py                   # combines benign + malicious header DataFrames -> CSV
  body_dataset_generator/
    download_data.py                   # downloads the base body dataset from HuggingFace
    hard_negative_df_generator.py      # loads manual hard-negative JSON -> DataFrame
    dataset_maker.py                   # combines hard negatives + base dataset -> CSV
trainers/
  header_trainer.py                    # trains, evaluates, and saves the header model
  body_trainer.py                      # trains, evaluates, and saves the body model
models/
  header_model.pkl
  body_model.pkl
notebooks/
  01_explore_dataset.ipynb             # dataset exploration and sanity checks
  02_evaluate_model.ipynb
```

## Datasets

### Header dataset

Built from two manually curated sources:

- **Benign headers** — extracted from real proxy traffic logs, deduplicated by header field/value pairs.
- **Malicious headers** — hand-authored examples across four attack categories: `model_override`, `system_prompt_injection`, `role_override`, `safety_bypass`.

Final composition: **53 samples** (33 benign / 20 malicious, 5 samples per attack category).

> **Known limitation:** 5 samples per attack category is small. The current header model likely generalizes to close variations (verified manually — a header value never seen in training, `claude-jailbroken-v3`, was still correctly flagged), but it hasn't been tested against a wide enough range of malicious header phrasing to be trusted as a final model. Expanding each attack category to 15–20+ samples is a planned next step before this model is considered production-ready.

### Body dataset

Combines two sources:

- **Base dataset** — [`neuralchemy/Prompt-injection-dataset`](https://huggingface.co/datasets/neuralchemy/Prompt-injection-dataset) from HuggingFace (`core` config, train + validation + test splits concatenated).
- **Hard negatives** — manually authored benign sentences that contain attack-adjacent vocabulary (`ignore`, `override`, `bypass`, `execute`, `inject`, etc.) in an entirely harmless context, e.g. *"You can safely ignore the warning about unused imports in this file."* These exist specifically to reduce false positives — without them, a model might learn to flag any sentence containing the word "ignore," regardless of context.

Final composition: several thousand samples, evaluated with a stratified 80/20 train/test split.

## Approach

### Feature extraction

Both models use `TfidfVectorizer`, but with different tokenization strategies:

- **Header model:** `analyzer="char_wb"` (character n-grams). Header values are short and ungrammatical, so meaning lives in substrings (e.g. `overr`, `bypa`, `jailb`) rather than whole words.
- **Body model:** `analyzer="word"` (word-level tokens). Request bodies are full sentences, so word-level meaning is more informative than character fragments.

### Model

Both models use `LogisticRegression` with `class_weight="balanced"` (to compensate for label imbalance) wrapped in a single `sklearn.Pipeline` alongside the vectorizer. This keeps preprocessing and modeling as one fit-able unit and avoids data leakage — the vectorizer is only ever fit on the training split, never on the full dataset.

Both datasets use `train_test_split(..., stratify=y)` to preserve class balance across the train/test split, which matters especially for the header dataset given its small size.

### Results

| | Body model | Header model |
|---|---|---|
| Test set size | 1,261 | 11 |
| Accuracy | 0.94 | 0.91 |
| Precision (malicious) | 0.95 | 0.80 |
| Recall (malicious) | 0.95 | 1.00 |

> **Read the header numbers with caution.** With only 11 test samples, a single misclassification shifts the reported metrics by ~9%. These numbers indicate the pipeline works end-to-end, not that the header model is production-grade. The body model's numbers are far more statistically meaningful given its larger test set.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the pipeline

**1. Build datasets:**

```bash
python -m src.header_dataset_gen.dataset_maker
python -m src.body_dataset_generator.dataset_maker
```

This downloads the base body dataset from HuggingFace, combines it with hard negatives, combines the header sources, and writes both final CSVs to `data/processed/`.

**2. Train models:**

```bash
python trainers/header_trainer.py
python trainers/body_trainer.py
```

Each script trains a pipeline, prints a `classification_report` on the held-out test split, then re-serializes the model and saves it to `models/`.

## Next steps

- Expand the header dataset (more malicious samples per attack category).
- Add unit tests for the dataset-generation modules.
- Wire the trained `.pkl` models into `analyzer.py` in the main LLM Inspector proxy.
- Consider a `group_id`-aware split for the body dataset if/when augmented samples are added, to avoid train/test leakage between near-duplicate augmented sentences.