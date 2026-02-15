from pathlib import Path
import pandas as pd


# Project root = folder containing "deployguard"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_PATH = PROJECT_ROOT / "data" / "processed" / "feature_snapshot.csv"


def load_latest_state():
    if not FEATURE_PATH.exists():
        raise FileNotFoundError(
            f"Feature file not found at {FEATURE_PATH}. "
            "Run ingestion + feature_engineering first."
        )

    df = pd.read_csv(FEATURE_PATH)

    required_columns = {"timestamp", "service", "latency", "risk_score"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns in feature_snapshot.csv: {missing}"
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    latest = (
        df.sort_values("timestamp")
          .groupby("service", as_index=False)
          .tail(1)
    )

    return latest
