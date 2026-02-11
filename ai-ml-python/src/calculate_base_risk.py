def calculate_base_risk(latency):
    baseline = {
        "order": 0.10,
        "payment": 0.10,
        "inventory": 0.05
    }

    base_risk = {}

    for service, value in latency.items():
        delta = max(0, (value - baseline[service]) / baseline[service])
        base_risk[service] = min(delta, 1.0)

    return base_risk
