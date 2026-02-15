import pandas as pd
import os


from deployguard.utils.paths import RAW_DIR, PROCESSED_DIR

RAW_PATH = RAW_DIR / "latency_snapshot.csv"
OUTPUT_PATH = PROCESSED_DIR / "feature_snapshot.csv"



def load_data():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError("Raw latency file not found.")

    df = pd.read_csv(RAW_PATH)

    if df.empty:
        raise ValueError("Raw dataset is empty.")

    required_cols = {"timestamp", "service", "latency_sum"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols}")

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", utc=True)

    # Rename latency column
    df = df.rename(columns={"latency_sum": "latency"})

    # Enforce numeric type
    df["latency"] = pd.to_numeric(df["latency"], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["service", "latency"])

    # Remove duplicates (same service + timestamp)
    df = df.drop_duplicates(subset=["service", "timestamp"])

    # Sort
    df = df.sort_values(["service", "timestamp"])

    return df


def compute_latency_delta(df):
    df["latency_delta"] = (
        df.groupby("service")["latency"].diff()
    )
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

    # Early rows fallback
    df["rolling_mean"] = df["rolling_mean"].fillna(df["latency"])
    df["rolling_std"] = df["rolling_std"].fillna(0)

    return df


def main():
    df = load_data()

    if df.empty:
        raise ValueError("No valid latency data found.")

    df = compute_latency_delta(df)
    df = compute_rolling_features(df, window=3)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Feature engineering completed.")
    print("Total rows:", len(df))
    print("Services detected:", df["service"].unique())
    print("Rows per service:")
    print(df.groupby("service").size())


if __name__ == "__main__":
    main()
