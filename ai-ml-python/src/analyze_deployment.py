from fetch_metrics import fetch_metrics
from calculate_base_risk import calculate_base_risk
from propagate_risk import propagate_risk
from explain_risk import explain_risk
from impact_report import generate_report


def analyze_deployment(service_name: str):
    latency = fetch_metrics()
    base_risk = calculate_base_risk(latency)

    final_risk = propagate_risk(
        base_risk=base_risk,
        source_service=service_name
    )

    explanation = explain_risk(
        source_service=service_name,
        final_risk=final_risk
    )

    report = generate_report(
        service_name=service_name,
        latency=latency,
        base_risk=base_risk,
        final_risk=final_risk,
        explanation=explanation
    )

    return report


if __name__ == "__main__":
    print(analyze_deployment("order"))
