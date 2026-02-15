"""
Service-level base risk computation.

PURE LOGIC:
- No file reads
- No printing
- Accepts latest_df
"""

def compute_service_risk(
    latest_df,
    spike_weight: float = 0.6,
    baseline_weight: float = 0.4
) -> dict:
    """
    Computes base risk per service.

    Args:
        latest_df (DataFrame): Latest snapshot per service
        spike_weight (float): Weight for spike contribution
        baseline_weight (float): Weight for baseline anomaly risk

    Returns:
        dict: {service_name: risk_score}
    """

    service_risk = {}

    for _, row in latest_df.iterrows():

        service = row["service"]
        risk_score = float(row["risk_score"])
        is_spike = int(row["is_spike"])

        # Baseline anomaly contribution
        baseline_component = risk_score * baseline_weight

        # Spike contribution scaled by anomaly intensity
        spike_component = spike_weight * risk_score if is_spike == 1 else 0

        risk = baseline_component + spike_component

        # Clamp to [0, 1]
        risk = min(max(risk, 0.0), 1.0)

        service_risk[service] = risk

    return service_risk
