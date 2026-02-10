import pandas as pd
from dependency_graph import get_upstream_chain

SERVICE_MAP = {
    "/inventory/check": "inventory",
    "/payment/pay": "payment",
    "/order/create": "order"
}

df = pd.read_csv("data/raw/latency_snapshot.csv")

latest = df.groupby("service").tail(1)

print("\n--- Risk Explanation ---\n")

for _, row in latest.iterrows():

    endpoint = row["service"]
    service_name = SERVICE_MAP.get(endpoint)

    if not service_name:
        print(endpoint, "unknown mapping")
        continue

    upstream_services = get_upstream_chain(service_name)

    if upstream_services:
        print(endpoint, "is impacted by:", upstream_services)
    else:
        print(endpoint, "has no upstream dependencies")
