# impact_report.py
"""
Impact report generator for DeployGuard v1.

Purpose:
- Combine latency, base risk, propagated risk, and explanations
- Produce a clean, structured report
- No printing, no I/O
"""


def generate_report(
    service_name: str,
    latency: dict,
    base_risk: dict,
    final_risk: dict,
    explanation: dict
) -> dict:
    """
    Generate the final deploy impact report.

    Args:
        service_name (str): Service being deployed
        latency (dict): Observed latency per service
        base_risk (dict): Base risk per service
        final_risk (dict): Propagated risk per service
        explanation (dict): Explanation per service

    Returns:
        dict: Structured deploy impact report
    """

    impacted_services = {
        svc: risk
        for svc, risk in final_risk.items()
        if svc != service_name and risk > 0
    }

    return {
        "service": service_name,
        "latency": latency,
        "base_risk": base_risk,
        "final_risk": final_risk,
        "blast_radius": impacted_services,
        "explanation": explanation
    }
def decide_verdict(final_risk):
    max_risk = max(final_risk.values())

    if max_risk >= 0.7:
        return "BLOCK"
    elif max_risk >= 0.4:
        return "WARN"
    else:
        return "SAFE"
