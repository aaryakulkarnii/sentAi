from app.services.risk_scoring import compute_risk_score


def test_critical_high_criticality():
    score = compute_risk_score("critical", 1.0, asset_criticality=5)
    assert score == 100


def test_low_severity_low_crit():
    score = compute_risk_score("low", 0.5, asset_criticality=1)
    assert 0 < score < 30


def test_exploit_multiplier():
    without = compute_risk_score("high", 1.0, asset_criticality=3, exploit_available=False)
    with_exploit = compute_risk_score("high", 1.0, asset_criticality=3, exploit_available=True)
    assert with_exploit > without
