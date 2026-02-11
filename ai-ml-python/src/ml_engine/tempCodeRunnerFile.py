import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "latency_snapshot.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "feature_snapshot.csv")


def normalize_service(uri: str):
    if isinstance(uri, str):
        if uri.startswith("/order"):
            return "order"
        if uri.startswith("/payment"):
            return "payment"
        if uri.startswith("/inventory"):
            return "inventory"
    return uri


def load_data():
    df = pd.read_csv(RAW_PATH)

    # Robust timestamp parsing (handles mixed +00:00 and non-timezone)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="mixed",
        utc=True
    )

    # Normalize service names
    df["service"] = df["service"].apply(normalize_service)

    # Sort correctly
    df = df.sort_values(["service", "timestamp"])

    return df


def compute_latency_delta(df):
    df["latency_delta"] = df.groupby("service")["latency_sum"].diff()
    df["latency_delta"] = df["latency_delta"].fillna(0)
    return df


def compute_rolling_features(df, window=3):

    df["rolling_mean"] = (
        df.groupby("service")["latency_sum"]
        .rolling(window)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["rolling_std"] = (
        df.groupby("service")["latency_sum"]
        .rolling(window)
        .std()
        .reset_index(level=0, drop=True)
    )

    df["rolling_mean"] = df["rolling_mean"].fillna(df["latency_sum"])
    df["rolling_std"] = df["rolling_std"].fillna(0)

    return df


def main():
    df = load_data()
    df = compute_latency_delta(df)
    df = compute_rolling_features(df)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Feature engineering completed.")
    print("Rows:", len(df))
    print("Columns:", df.columns.tolist())


if __name__ == "__main__":
    main()
