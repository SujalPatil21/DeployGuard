"""
Explain why each service is risky based on dependency propagation.

PURE LOGIC:
- No printing
- No file reads
- No hardcoded services
- Uses live dependency graph
"""

from deployguard.core.dependency_graph import get_graph
import networkx as nx


def explain_risk(source_service: str, final_risk: dict) -> dict:
    """
    Generates explanation for service risk.

    Args:
        source_service (str): Service being deployed
        final_risk (dict): Final propagated risk per service

    Returns:
        dict: Explanation per service
    """

    graph = get_graph()
    explanation = {}

    for service in final_risk.keys():

        if service == source_service:
            explanation[service] = "Source of deployment change"
            continue

        upstreams = list(nx.ancestors(graph, service))

        if source_service in upstreams:
            explanation[service] = (
                f"Impacted due to upstream dependency on '{source_service}'"
            )
        else:
            explanation[service] = "No direct upstream dependency impact"

    return explanation
