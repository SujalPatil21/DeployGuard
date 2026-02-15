import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "labeled_dataset.csv"
)

MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "deployment_risk_model.pkl")


def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            "labeled_dataset.csv not found. Run label_generator first."
        )

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        raise ValueError("labeled_dataset.csv is empty.")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df


def train():

    df = load_data()

    # Drop timestamp (not predictive)
    df = df.drop(columns=["timestamp"])

    if "failure" not in df.columns:
        raise ValueError("Target column 'failure' missing.")

    # Show class distribution
    print("\nClass Distribution:")
    print(df["failure"].value_counts())

    X = df.drop(columns=["failure"])
    y = df["failure"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("\nModel saved to:", MODEL_PATH)


if __name__ == "__main__":
    train()
