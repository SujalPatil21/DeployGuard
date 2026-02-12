import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "latency_snapshot.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "feature_snapshot.csv")


def normalize_service(service: str):
    if isinstance(service, str):
        if service.startswith("order"):
            return "order"
        if service.startswith("payment"):
            return "payment"
        if service.startswith("inventory"):
            return "inventory"
    return service


def load_data():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError("Raw latency file not found.")

    df = pd.read_csv(RAW_PATH)

    if df.empty:
        raise ValueError("Raw dataset is empty.")

    # Parse timestamps safely
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", utc=True)

    # Rename latency column if still old name
    if "latency_sum" in df.columns:
        df = df.rename(columns={"latency_sum": "latency"})

    # Normalize service names
    df["service"] = df["service"].apply(normalize_service)

    # Sort per service and time
    df = df.sort_values(["service", "timestamp"])

    return df


def compute_latency_delta(df):
    df["latency_delta"] = df.groupby("service")["latency"].diff()
    df["latency_delta"] = df["latency_delta"].fillna(0)
    return df


def compute_rolling_features(df, window=20):
    df["rolling_mean"] = (
        df.groupby("service")["latency"]
        .rolling(window)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["rolling_std"] = (
        df.groupby("service")["latency"]
        .rolling(window)
        .std()
        .reset_index(level=0, drop=True)
    )

    # Fill early NaNs
    df["rolling_mean"] = df["rolling_mean"].fillna(df["latency"])
    df["rolling_std"] = df["rolling_std"].fillna(0)

    return df


def main():
    df = load_data()
    df = df.dropna(subset=["latency"])
    df = compute_latency_delta(df)
    df = compute_rolling_features(df, window=20)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Feature engineering completed.")
    print("Total rows:", len(df))
    print("Rows per service:")
    print(df.groupby("service").size())

    print("\nLatency stats per service:")
    print(df.groupby("service")["latency"].agg(["min", "max", "mean", "std"]))


if __name__ == "__main__":
    main()
