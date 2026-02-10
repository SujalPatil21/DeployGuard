import pandas as pd
from dependency_graph import get_upstream_chain

df = pd.read_csv("data/raw/latency_snapshot.csv")

latest = df.groupby("service").tail(1)

for _, row in latest.iterrows():
    service = row["service"].replace("/", "").split("/")[0]
    impact = get_upstream_chain(service)
    print(service, "affects", impact)
