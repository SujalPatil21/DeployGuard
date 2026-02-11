"""
Explain why each service is risky based on dependency propagation.
This module is PURE logic:
- No printing
- No file reads
- No side effects
"""

# Logical dependency model for v1 (URI-level services)
DEPENDENCIES = {
    "order": [],
    "payment": ["order"],
    "inventory": ["payment", "order"]
}


def explain_risk(source_service: str, final_risk: dict) -> dict:
    """
    Generates a human-readable explanation for service risk.

    Args:
        source_service (str): Service being deployed (e.g. "order")
        final_risk (dict): Final propagated risk per service

    Returns:
        dict: Explanation per service
    """

    explanation = {}

    for service in final_risk.keys():
        if service == source_service:
            explanation[service] = "Source of deployment change"
        else:
            upstreams = DEPENDENCIES.get(service, [])
            if upstreams:
                explanation[service] = (
                    f"Impacted due to upstream dependency: {upstreams}"
                )
            else:
                explanation[service] = "No upstream dependency impact"

    return explanation
