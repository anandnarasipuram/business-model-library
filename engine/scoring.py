"""Weighted scoring and stage helpers for portfolio opportunities."""

DEFAULT_WEIGHTS = {
    "value": 0.35,
    "feasibility": 0.25,
    "strategic_fit": 0.25,
    "time_to_result": 0.15,
}

STAGE_ORDER = ["Explore", "Validate", "Scale", "Stop"]

STAGE_COLORS = {
    "Explore": "#7A8CA3",
    "Validate": "#C9A55A",
    "Scale": "#2E7D5B",
    "Stop": "#B33A3A",
}


def weighted_score(scores: dict, weights: dict = None) -> float:
    """Compute a 1-5 weighted score from a scores dict and a weights dict."""
    weights = weights or DEFAULT_WEIGHTS
    total_weight = sum(weights.values()) or 1.0
    total = sum(scores.get(key, 0) * weight for key, weight in weights.items())
    return round(total / total_weight, 2)


def score_opportunities(opportunities: list, weights: dict = None) -> list:
    """Return opportunities annotated with a computed weighted_score field."""
    annotated = []
    for opp in opportunities:
        opp = dict(opp)
        opp["weighted_score"] = weighted_score(opp.get("scores", {}), weights)
        annotated.append(opp)
    return annotated
