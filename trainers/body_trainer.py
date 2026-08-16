from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
import joblib


BODY_DATASET_PATH = Path(__file__).parent.parent / "data" / "processed" / "body_dataset.csv"
BODY_MODEL_PATH = Path(__file__).parent.parent / "models"


def load_dataset(path: Path):
    body_df = pd.read_csv(path)
    body_df_final = body_df[["text", "label"]]
    x = body_df_final["text"].astype(str).to_numpy()
    y = body_df_final["label"].to_numpy()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
    return x_train, x_test, y_train, y_test



if __name__ == "__main__":
    x_train, x_test, y_train, y_test = load_dataset(BODY_DATASET_PATH)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="word")),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000)),
    ])
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)

    print(pipeline.score(x_train, y_train))
    print(pipeline.score(x_test, y_test))
    print(classification_report(y_test, y_pred, target_names=["benign", "malicious"]))
    BODY_MODEL_PATH.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, BODY_MODEL_PATH / "body_model.pkl")
    print(f"Model saved to {BODY_MODEL_PATH / 'body_model.pkl'}")



