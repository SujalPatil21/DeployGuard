import networkx as nx
from deployguard.core.dependency_graph import G


def compute_graph_features():
    """
    Compute structural graph features for each service node.

    Returns:
        dict: {
            service_name: {
                upstream_count: int,
                downstream_count: int,
                in_degree: int,
                out_degree: int
            }
        }
    """

    features = {}

    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())

    for node in G.nodes():

        upstream = nx.ancestors(G, node)
        downstream = nx.descendants(G, node)

        features[node] = {
            "upstream_count": len(upstream),
            "downstream_count": len(downstream),
            "in_degree": in_degrees.get(node, 0),
            "out_degree": out_degrees.get(node, 0),
        }

    return features
