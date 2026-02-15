"""
Impact report generator for DeployGuard.

Purpose:
- Combine latency, base risk, propagated risk, and explanations
- Produce a clean, structured report
- Pure logic (no printing, no I/O)
"""


def generate_report(
    service_name: str,
    latency: dict,
    base_risk: dict,
    final_risk: dict,
    explanation: dict
) -> dict:

    if not final_risk:
        raise ValueError("final_risk cannot be empty.")

    # Sort services by descending risk
    sorted_risk = dict(
        sorted(final_risk.items(), key=lambda x: x[1], reverse=True)
    )

    impacted_services = {
        svc: risk
        for svc, risk in sorted_risk.items()
        if svc != service_name and risk > 0
    }

    max_risk = max(sorted_risk.values())

    return {
        "service": service_name,
        "latency": latency,
        "base_risk": base_risk,
        "final_risk": sorted_risk,
        "blast_radius": impacted_services,
        "max_risk": max_risk,
        "explanation": explanation
    }


def decide_verdict(final_risk: dict) -> str:

    if not final_risk:
        return "SAFE"

    max_risk = max(final_risk.values())

    if max_risk >= 0.7:
        return "BLOCK"
    elif max_risk >= 0.4:
        return "WARN"
    else:
        return "SAFE"
