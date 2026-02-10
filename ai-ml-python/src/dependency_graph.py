import networkx as nx

G = nx.DiGraph()

G.add_edges_from([
    ("order", "payment"),
    ("payment", "inventory")
])

def get_impact_chain(service):
    return list(nx.descendants(G, service))

def get_upstream_chain(service):
    return list(nx.ancestors(G, service))
