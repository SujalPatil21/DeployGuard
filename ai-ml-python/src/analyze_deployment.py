from ml_engine.feature_engineering import main as run_feature_engineering
from detect_latency_anomaly import main as run_anomaly_detection
from propagate_risk import load_latest_state, propagate_risk
from explain_risk import explain_risk
from impact_report import generate_report, decide_verdict


def analyze_deployment(service_name: str):

    # Step 1: Feature Engineering
    run_feature_engineering()

    # Step 2: Anomaly Detection
    run_anomaly_detection()

    # Step 3: Load Latest State
    latest_df = load_latest_state()

    latency = {
        row["service"]: row["latency"]
        for _, row in latest_df.iterrows()
    }

    # Step 4: Risk Propagation
    final_risk = propagate_risk(latest_df)

    # Step 5: Explanation
    explanation = explain_risk(service_name, final_risk)

    # Step 6: Report
    report = generate_report(
        service_name=service_name,
        latency=latency,
        base_risk=None,
        final_risk=final_risk,
        explanation=explanation
    )

    verdict = decide_verdict(final_risk)

    report["verdict"] = verdict

    return report


if __name__ == "__main__":
    result = analyze_deployment("payment")
    print(result)
