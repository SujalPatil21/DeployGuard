"""
Risk propagation engine.

PURE LOGIC:
- No printing
- No file access
- No hardcoded services
- Uses live dependency graph
"""

from deployguard.core.dependency_graph import get_graph
import networkx as nx


def propagate_risk_from_dict(base_service_risk: dict, decay: float = 0.6) -> dict:
    """
    Propagates service risk upstream through dependency graph.

    Args:
        base_service_risk (dict): {service_name: base_risk}
        decay (float): Risk decay factor per hop

    Returns:
        dict: Final propagated risk per service
    """

    graph = get_graph()
    final_risk = dict(base_service_risk)

    for service, base_risk in base_service_risk.items():

        if base_risk <= 0:
            continue

        upstream_services = nx.ancestors(graph, service)

        for upstream in upstream_services:
            propagated = base_risk * decay

            final_risk[upstream] = max(
                final_risk.get(upstream, 0),
                propagated
            )

    return final_risk
