import pandas as pd
from dependency_graph import get_upstream_chain

FEATURE_PATH = "data/processed/feature_snapshot.csv"


def load_latest_state():
    df = pd.read_csv(FEATURE_PATH)

    if "risk_score" not in df.columns:
        raise ValueError("Run detect_latency_anomaly.py first.")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    latest = df.sort_values("timestamp").groupby("service").tail(1)

    return latest


def propagate_risk(latest_df, decay=0.6, spike_boost=1.2):

    final_risk = {}

    # Step 1: Base risk from anomaly engine
    for _, row in latest_df.iterrows():
        service = row["service"]

        base_risk = row["risk_score"]

        # Boost risk if true spike
        if row["is_spike"] == 1:
            base_risk *= spike_boost

        base_risk = min(base_risk, 1.0)

        final_risk[service] = base_risk

    # Step 2: Propagate upstream
    for service, base_risk in list(final_risk.items()):

        if base_risk > 0:
            upstream_services = get_upstream_chain(service)

            for upstream in upstream_services:
                propagated = base_risk * decay
                final_risk[upstream] = max(
                    final_risk.get(upstream, 0),
                    propagated
                )

    return final_risk


def main():
    latest = load_latest_state()
    final_risk = propagate_risk(latest)

    print("\n===== PROPAGATED RISK =====")
    for svc, risk in final_risk.items():
        print(f"{svc}: {risk:.4f}")


if __name__ == "__main__":
    main()
