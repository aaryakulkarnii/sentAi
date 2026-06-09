"""Compute 0–100 risk score for an incident."""

SEVERITY_WEIGHT = {"low": 10, "medium": 30, "high": 60, "critical": 100}
CRITICALITY_MULT = {1: 0.6, 2: 0.8, 3: 1.0, 4: 1.2, 5: 1.5}


def compute_risk_score(
    severity: str,
    confidence: float,
    asset_criticality: int = 3,
    exploit_available: bool = False,
) -> int:
    base = SEVERITY_WEIGHT.get(severity, 10) * confidence
    score = base * CRITICALITY_MULT.get(asset_criticality, 1.0)
    if exploit_available:
        score *= 1.3
    return min(100, int(score))
