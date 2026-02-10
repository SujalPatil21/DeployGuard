from dependency_graph import get_impact_chain, get_upstream_chain

print(get_upstream_chain("inventory"))
print(get_impact_chain("order"))
