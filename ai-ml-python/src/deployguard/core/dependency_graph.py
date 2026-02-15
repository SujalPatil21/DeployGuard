from pathlib import Path
import json
import networkx as nx
from deployguard.utils.paths import CONFIG_DIR

CONFIG_PATH = CONFIG_DIR / "dependency_config.json"


def load_graph() -> nx.DiGraph:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Dependency config not found at {CONFIG_PATH}"
        )

    with open(CONFIG_PATH, "r") as f:
        edges = json.load(f)

    if not isinstance(edges, list):
        raise ValueError("Dependency config must be a list of [source, target] pairs.")

    G = nx.DiGraph()

    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"Invalid edge format: {edge}")
        G.add_edge(edge[0], edge[1])

    return G


# Singleton-style lazy graph
_GRAPH = None


def get_graph() -> nx.DiGraph:
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = load_graph()
    return _GRAPH


def get_upstream(service: str):
    return list(get_graph().ancestors(service))


def get_downstream(service: str):
    return list(get_graph().descendants(service))
