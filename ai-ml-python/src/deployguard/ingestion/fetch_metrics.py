import requests
import datetime
import csv
import os
import math
from deployguard.utils.paths import RAW_DIR

PROM_URL = "http://localhost:9090/api/v1/query"

QUERY = """
(
  sum by (uri) (
    rate(http_server_requests_seconds_sum{
      uri!="/actuator/prometheus",
      uri!="/**"
    }[30s])
  )
)
/
(
  sum by (uri) (
    rate(http_server_requests_seconds_count{
      uri!="/actuator/prometheus",
      uri!="/**"
    }[30s])
  )
)
"""

OUTPUT_PATH = RAW_DIR / "latency_snapshot.csv"


def map_uri_to_service(uri: str):
    """
    Dynamically extract service name from URI.
    Example:
        /order/create     -> order
        /payment/pay      -> payment
        /billing/charge   -> billing
    """
    if not uri or not uri.startswith("/"):
        return None

    parts = uri.split("/")
    if len(parts) > 1:
        return parts[1]

    return None


def fetch_metrics():
    response = requests.get(PROM_URL, params={"query": QUERY}, timeout=5)
    response.raise_for_status()

    data = response.json()
    result = data["data"]["result"]

    timestamp = datetime.datetime.now(datetime.UTC)

    service_latency = {}

    for row in result:
        uri = row["metric"].get("uri", "")
        value = float(row["value"][1])

        service = map_uri_to_service(uri)

        if service and not math.isnan(value):
            service_latency[service] = value

    metrics = []

    for svc, value in service_latency.items():
        metrics.append({
            "timestamp": timestamp,
            "service": svc,
            "latency_sum": value
        })

    return metrics


def append_to_csv(rows):
    file_exists = os.path.isfile(OUTPUT_PATH)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, mode="a", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["timestamp", "service", "latency_sum"]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)


def main():
    print("Writing to:", OUTPUT_PATH)

    rows = fetch_metrics()

    if rows:
        append_to_csv(rows)
        print("Metrics collected:", rows)
    else:
        print("No valid metrics returned.")


if __name__ == "__main__":
    main()
