import pandas as pd

df = pd.read_csv("data/raw/latency_snapshot.csv")

# Keep only rows where latency is non-zero
nz = df[df["latency_sum"] > 0]

latest = nz.groupby("service").tail(1).set_index("service")["latency_sum"]
previous = nz.groupby("service").nth(-2).set_index("service")["latency_sum"]

delta = (latest - previous).fillna(0)
risk = (delta / (previous + 1e-6)).sort_values(ascending=False)

print("\nLatency Delta:\n", delta)
print("\nRelative Risk Score:\n", risk)
print("\nHighest Risk Service:", risk.idxmax())
