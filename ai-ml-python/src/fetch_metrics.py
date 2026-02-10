import requests
import pandas as pd
import time
from datetime import datetime

PROM_URL = "http://localhost:9090/api/v1/query"
query = 'sum by (uri) (rate(http_server_requests_seconds_sum{uri!="/actuator/prometheus"}[5m]))'

# Create file ONE TIME with header
pd.DataFrame(columns=["timestamp","service","latency_sum"]).to_csv(
    "data/raw/latency_snapshot.csv", index=False
)

while True:

    response = requests.get(PROM_URL, params={'query': query})
    data = response.json()

    records = []

    for result in data['data']['result']:
        metric = result['metric']
        value = result['value'][1]
        records.append({
            "timestamp": datetime.now(),
            "service": metric.get("uri"),
            "latency_sum": float(value)
        })

    df = pd.DataFrame(records)

    # Append WITHOUT header now
    df.to_csv("data/raw/latency_snapshot.csv", mode='a', header=False, index=False)

    print(df)

    time.sleep(30)
