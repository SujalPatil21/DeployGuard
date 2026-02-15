from deployguard.ml_engine.feature_engineering import main as run_feature_engineering
from deployguard.core.detect_latency_anomaly import main as run_anomaly_detection
from deployguard.core.service_risk_engine import compute_service_risk
from deployguard.core.propagate_risk import propagate_risk_from_dict
from deployguard.core.data_loader import load_latest_state
from deployguard.core.explain_risk import explain_risk
from deployguard.reporting.impact_report import generate_report, decide_verdict


def analyze_deployment(service_name: str):

    # Step 1 – Feature Engineering
    run_feature_engineering()

    # Step 2 – Anomaly Detection
    run_anomaly_detection()

    # Step 3 – Load Latest State
    latest_df = load_latest_state()

    latency = {
        row["service"]: row["latency"]
        for _, row in latest_df.iterrows()
    }

    # Step 4 – Compute Base Risk
    base_service_risk = compute_service_risk(latest_df)

    # Step 5 – Propagate Risk
    final_risk = propagate_risk_from_dict(base_service_risk)

    # Step 6 – Explain Risk
    explanation = explain_risk(service_name, final_risk)

    # Step 7 – Generate Report
    report = generate_report(
        service_name=service_name,
        latency=latency,
        base_risk=base_service_risk,
        final_risk=final_risk,
        explanation=explanation
    )

    verdict = decide_verdict(final_risk)
    report["verdict"] = verdict

    return report
