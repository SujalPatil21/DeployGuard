import pandas as pd
from dependency_graph import get_upstream_chain

SERVICE_MAP = {
    "/inventory/check": "inventory",
    "/payment/pay": "payment",
    "/order/create": "order"
}

df = pd.read_csv("data/raw/latency_snapshot.csv")

latest = df.groupby("service").tail(1).set_index("service")

print("\n===== DEPLOY IMPACT REPORT =====\n")

for endpoint, row in latest.iterrows():

    service_name = SERVICE_MAP[endpoint]
    risk = row["latency_sum"]
    upstream = get_upstream_chain(service_name)

    print("Service:", endpoint)
    print("Risk Score:", round(risk, 6))

    if upstream:
        print("Impacted By:", upstream)
    else:
        print("Impacted By: None")

    print("---------------------------")
