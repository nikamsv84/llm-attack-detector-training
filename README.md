# LLM Inspector — Attack Detector Training

Training pipeline for the AI Attack Detector used in [LLM Inspector](<لینک ریپوی اصلی>).
Generates a dataset covering both request bodies and HTTP headers, and fits a
prompt-injection detection model with scikit-learn.

## Structure
- `src/download_data.py` — downloads base prompt-injection dataset from Hugging Face
- `src/dataset_gen/` — generates synthetic header-based attack samples
- `notebooks/` — dataset exploration and model evaluation
- `models/` — trained model output (not committed; see Releases)

## Status
🚧 Work in progress
- hard negative is for preventing false positive and model overfitting.