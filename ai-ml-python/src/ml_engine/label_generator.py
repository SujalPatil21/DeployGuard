import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "feature_snapshot.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "labeled_dataset.csv")


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


def detect_spike(row, z_threshold=1.5):
    if row["rolling_std"] == 0:
        return False

    z_score = (row["latency"] - row["rolling_mean"]) / row["rolling_std"]
    return z_score > z_threshold


def generate_labels(df):
    df["failure"] = 0
    time_window = pd.Timedelta(seconds=60)

    for service in df["service"].unique():

        service_rows = df[df["service"] == service]

        downstream_services = DEPENDENCIES.get(service, [])

        for idx, current_row in service_rows.iterrows():

            if detect_spike(current_row):

                timestamp = current_row["timestamp"]

                for downstream in downstream_services:

                    downstream_rows = df[
                        (df["service"] == downstream) &
                        (df["timestamp"] > timestamp) &
                        (df["timestamp"] <= timestamp + time_window)
                    ]

                    # If ANY downstream latency increases meaningfully
                    for _, downstream_row in downstream_rows.iterrows():

                        if downstream_row["latency"] > downstream_row["rolling_mean"]:
                            df.loc[idx, "failure"] = 1
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
