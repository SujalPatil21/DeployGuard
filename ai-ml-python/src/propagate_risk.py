import pandas as pd
from dependency_graph import get_impact_chain

df = pd.read_csv("data/raw/latency_snapshot.csv")

latest = df.groupby("service").last()["latency_sum"]

risk_scores = latest.copy()

for service in latest.index:
    svc = service.split("/")[1]   # convert /payment/pay → payment
    impacted = get_impact_chain(svc)

    for imp in impacted:
        key = f"/{imp}"
        for existing in risk_scores.index:
            if imp in existing:
                risk_scores[existing] += latest[service] * 0.5

print("\nBase Risk:")
print(latest)

print("\nPropagated Risk:")
print(risk_scores.sort_values(ascending=False))
