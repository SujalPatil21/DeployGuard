import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "feature_snapshot.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "labeled_dataset.csv")


# MUST match normalized service names
DEPENDENCIES = {
    "order": ["payment"],
    "payment": ["inventory"],
    "inventory": []
}


def load_data():
    df = pd.read_csv(INPUT_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["service", "timestamp"])

    return df


def detect_spike(row):
    threshold = row["rolling_mean"] + 1 * row["rolling_std"]

    return (
        row["latency_delta"] > threshold and
        row["latency_delta"] > 0.05
    )


def generate_labels(df):
    df["failure"] = 0

    time_window = pd.Timedelta(seconds=60)

    grouped = df.groupby("service")

    for service, group in grouped:

        downstream_services = DEPENDENCIES.get(service, [])

        for i in range(len(group)):

            current_row = group.iloc[i]

            if detect_spike(current_row):

                timestamp = current_row["timestamp"]

                for downstream in downstream_services:

                    downstream_rows = df[
                        (df["service"] == downstream) &
                        (df["timestamp"] > timestamp) &
                        (df["timestamp"] <= timestamp + time_window)
                    ]

                    for _, row in downstream_rows.iterrows():
                        if detect_spike(row):
                            df.loc[current_row.name, "failure"] = 1
                            break

    return df


def main():
    df = load_data()
    df = generate_labels(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print("Label generation complete.")
    print("Total rows:", len(df))
    print("Failures:", df["failure"].sum())


if __name__ == "__main__":
    main()
