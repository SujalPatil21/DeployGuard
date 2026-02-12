import requests
import datetime
import csv
import os


PROM_URL = "http://localhost:9090/api/v1/query"

# No filtering in PromQL — keep it simple
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




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "latency_snapshot.csv")


def map_uri_to_service(uri: str):
    if uri.startswith("/order"):
        return "order"
    if uri.startswith("/payment"):
        return "payment"
    if uri.startswith("/inventory"):
        return "inventory"
    return None


def fetch_metrics():
    response = requests.get(PROM_URL, params={"query": QUERY}, timeout=5)
    response.raise_for_status()

    data = response.json()
    print("RAW PROM RESPONSE:", data)

    result = data["data"]["result"]

    metrics = []
    timestamp = datetime.datetime.now(datetime.UTC)

    for row in result:
        uri = row["metric"].get("uri", "")
        value = float(row["value"][1])

        service = map_uri_to_service(uri)

        if service:
            metrics.append({
                "timestamp": timestamp,
                "service": service,
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

        for row in rows:
            writer.writerow(row)


def main():
    rows = fetch_metrics()

    if rows:
        append_to_csv(rows)
        print("Metrics collected:", rows)
    else:
        print("No valid metrics returned.")


if __name__ == "__main__":
    main()
