import pandas as pd
import numpy as np
import os

FEATURE_PATH = "data/processed/feature_snapshot.csv"


def compute_anomaly(df, z_threshold=1.5):
    # Drop corrupted rows
    df = df.dropna(subset=["latency", "rolling_mean", "rolling_std"])

    # Avoid division by zero
    df["safe_std"] = df["rolling_std"].replace(0, 1e-6)

    # Z-score calculation
    df["z_score"] = (df["latency"] - df["rolling_mean"]) / df["safe_std"]

    # Spike detection
    df["is_spike"] = (df["z_score"] > z_threshold).astype(int)

    # Convert z-score into bounded risk score (0 to 1)
    df["risk_score"] = 1 / (1 + np.exp(-df["z_score"]))  # sigmoid

    return df


def main():
    if not os.path.exists(FEATURE_PATH):
        raise FileNotFoundError("Run feature_engineering.py first.")

    df = pd.read_csv(FEATURE_PATH)

    # Parse timestamp safely
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    required_cols = ["latency", "rolling_mean", "rolling_std"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = compute_anomaly(df)

    # Clean NaNs before saving
    df = df.fillna(0)

    df.to_csv(FEATURE_PATH, index=False)

    print("\n===== ANOMALY DETECTION REPORT =====")
    print("Total rows:", len(df))
    print("Total spikes detected:", df["is_spike"].sum())

    print("\nLatest state per service:")
    latest = df.sort_values("timestamp").groupby("service").tail(1)
    print(latest[["service", "latency", "z_score", "risk_score", "is_spike"]])


if __name__ == "__main__":
    main()
