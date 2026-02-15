import os
import pandas as pd
import networkx as nx

from deployguard.core.dependency_graph import G
from deployguard.ml_engine.graph_feature_engine import compute_graph_features


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

INPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "feature_snapshot.csv"
)

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "labeled_dataset.csv"
)


def load_data():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            "feature_snapshot.csv not found. Run feature_engineering first."
        )

    df = pd.read_csv(INPUT_PATH)

    if df.empty:
        raise ValueError("feature_snapshot.csv is empty.")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["service", "timestamp"])

    return df


def compute_z_score(row):
    if row["rolling_std"] == 0:
        return 0
    return (row["latency"] - row["rolling_mean"]) / row["rolling_std"]


def detect_spike(row, z_threshold=1.5):
    return compute_z_score(row) > z_threshold


def generate_labels(df):

    df["failure"] = 0
    df["z_score"] = df.apply(compute_z_score, axis=1)

    time_window = pd.Timedelta(seconds=60)

    for service in df["service"].unique():

        service_rows = df[df["service"] == service]

        # If service not in graph, skip
        if service not in G.nodes:
            continue

        downstream_services = nx.descendants(G, service)

        for idx, current_row in service_rows.iterrows():

            if detect_spike(current_row):

                timestamp = current_row["timestamp"]

                for downstream in downstream_services:

                    downstream_rows = df[
                        (df["service"] == downstream)
                        & (df["timestamp"] > timestamp)
                        & (df["timestamp"] <= timestamp + time_window)
                    ]

                    for _, downstream_row in downstream_rows.iterrows():

                        downstream_z = compute_z_score(downstream_row)

                        if (
                            downstream_row["latency_delta"] > 0
                            and downstream_z > 1.0
                        ):
                            df.loc[idx, "failure"] = 1
                            break

    return df


def add_graph_features(df):

    graph_features = compute_graph_features()

    df["upstream_count"] = df["service"].map(
        lambda s: graph_features.get(s, {}).get("upstream_count", 0)
    )

    df["downstream_count"] = df["service"].map(
        lambda s: graph_features.get(s, {}).get("downstream_count", 0)
    )

    df["in_degree"] = df["service"].map(
        lambda s: graph_features.get(s, {}).get("in_degree", 0)
    )

    df["out_degree"] = df["service"].map(
        lambda s: graph_features.get(s, {}).get("out_degree", 0)
    )

    return df


def main():

    df = load_data()

    df = generate_labels(df)
    df = add_graph_features(df)

    # Remove service for architecture-agnostic ML
    df = df.drop(columns=["service"])

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Label generation complete.")
    print("Total rows:", len(df))
    print("Failures:", df["failure"].sum())


if __name__ == "__main__":
    main()
