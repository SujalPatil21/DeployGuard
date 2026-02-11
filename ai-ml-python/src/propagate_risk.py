# propagate_risk.py

DEPENDENCIES = {
    "order": ["payment"],
    "payment": ["inventory"],
    "inventory": []
}

def propagate_risk(base_risk, source_service):
    # Start with base risk
    final_risk = dict(base_risk)

    # BFS for risk propagation
    queue = [(source_service, 0)]

    while queue:
        current, depth = queue.pop(0)

        for child in DEPENDENCIES[current]:
            propagated = final_risk[current] * (1 / (depth + 2))
            final_risk[child] += propagated
            queue.append((child, depth + 1))

    # Clamp risk to [0, 1]
    for service in final_risk:
        final_risk[service] = min(final_risk[service], 1.0)

    return final_risk
