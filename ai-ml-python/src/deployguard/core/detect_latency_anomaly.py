from pathlib import Path
import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_PATH = PROJECT_ROOT / "data" / "processed" / "feature_snapshot.csv"

def compute_anomaly(df: pd.DataFrame, z_threshold: float = 1.5) -> pd.DataFrame:
    df = df.copy()

    required_cols = ["latency", "rolling_mean", "rolling_std", "latency_delta"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = df.dropna(subset=required_cols)

    z_scores = []
    spikes = []

    for _, row in df.iterrows():
        std = row["rolling_std"]

        # Fallback for insufficient history
        if std == 0:
            if abs(row["latency_delta"]) > 0.3:
                z = 3.0
                spike = 1
            else:
                z = 0.0
                spike = 0
        else:
            z = (row["latency"] - row["rolling_mean"]) / std
            spike = int(abs(z) > z_threshold)

        z_scores.append(z)
        spikes.append(spike)

    df["z_score"] = z_scores
    df["is_spike"] = spikes

    # Risk score (sigmoid bounded 0–1)
    df["risk_score"] = 1 / (1 + np.exp(-df["z_score"]))

    return df



def run_anomaly_detection() -> pd.DataFrame:
    if not FEATURE_PATH.exists():
        raise FileNotFoundError("Run feature_engineering first.")

    df = pd.read_csv(FEATURE_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    df = compute_anomaly(df)

    df.to_csv(FEATURE_PATH, index=False)

    print("\n===== ANOMALY DETECTION REPORT =====")
    print("Total rows:", len(df))
    print("Total spikes detected:", df["is_spike"].sum())

    latest = df.sort_values("timestamp").groupby("service").tail(1)
    print("\nLatest state per service:")
    print(latest[["service", "latency", "z_score", "risk_score", "is_spike"]])

    return df


if __name__ == "__main__":
    run_anomaly_detection()
