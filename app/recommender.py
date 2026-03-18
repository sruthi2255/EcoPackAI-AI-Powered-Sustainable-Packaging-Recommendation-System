import os
import numpy as np
from .schemas import QueryInput, RecommendationOut, RecommendationPayload

# ─── Currency conversion ──────────────────────────────────────────────────────
USD_TO_INR = 83.0   # 1 USD = ₹83  (update this as needed)

# ─── Uncomment when your .pkl files are ready ────────────────────────────────
# import joblib
# MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
# rf_model      = joblib.load(os.path.join(MODEL_DIR, "rf_cost_model.pkl"))
# xgb_model     = joblib.load(os.path.join(MODEL_DIR, "xgb_co2_model.pkl"))
# scaler        = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))

# ─── Material pool ───────────────────────────────────────────────────────────
MATERIALS = [
    {"material_type": "Heavy Duty Corrugated",   "base_cost_usd": 2.80, "co2": 0.95, "bio": 88, "rec": 94},
    {"material_type": "Biodegradable Foam",       "base_cost_usd": 3.20, "co2": 0.60, "bio": 95, "rec": 80},
    {"material_type": "Recycled Kraft Paper",     "base_cost_usd": 1.90, "co2": 0.45, "bio": 98, "rec": 99},
    {"material_type": "Mushroom Packaging",       "base_cost_usd": 4.10, "co2": 0.30, "bio": 100,"rec": 85},
    {"material_type": "Plant-Based PLA Film",     "base_cost_usd": 2.50, "co2": 0.55, "bio": 92, "rec": 78},
    {"material_type": "Recycled Plastic (rPET)",  "base_cost_usd": 1.60, "co2": 1.10, "bio": 40, "rec": 95},
    {"material_type": "Honeycomb Paperboard",     "base_cost_usd": 2.20, "co2": 0.70, "bio": 90, "rec": 96},
    {"material_type": "Air Pillow (recycled PE)", "base_cost_usd": 1.30, "co2": 1.20, "bio": 30, "rec": 88},
]


def _encode_level(level: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}.get(level.lower(), 2)


def _build_features(query, material):
    budget_usd = (query.budget_inr / USD_TO_INR) if query.budget_inr else 5.0
    return np.array([
        query.product_weight_kg,
        _encode_level(query.fragility_level),
        _encode_level(query.moisture_sensitivity),
        query.shipping_distance_km,
        budget_usd,
        material["base_cost_usd"],
        material["co2"],
        material["bio"],
        material["rec"],
    ]).reshape(1, -1)


def _predict_cost_inr(features, material):
    # REPLACE with: return float(rf_model.predict(features)[0]) * USD_TO_INR
    base_usd = material["base_cost_usd"]
    cost_usd = round(base_usd * (1 + features[0][0] * 0.05 + features[0][3] * 0.0001), 2)
    return round(cost_usd * USD_TO_INR, 2)


def _predict_co2(features, material):
    # REPLACE with: return float(xgb_model.predict(features)[0])
    base = material["co2"]
    return round(base * (1 + features[0][3] * 0.0002), 3)


def _suitability_score(query, material, cost_inr, co2):
    weights = {
        "eco":      {"bio": 0.35, "rec": 0.30, "co2": 0.25, "cost": 0.10},
        "cost":     {"bio": 0.10, "rec": 0.10, "co2": 0.15, "cost": 0.65},
        "balanced": {"bio": 0.25, "rec": 0.25, "co2": 0.25, "cost": 0.25},
    }.get(query.priority.lower(), {"bio": 0.25, "rec": 0.25, "co2": 0.25, "cost": 0.25})

    bio_norm  = material["bio"] / 100
    rec_norm  = material["rec"] / 100
    co2_norm  = 1 - min(co2 / 2.0, 1)
    cost_norm = 1 - min(cost_inr / 500.0, 1)   # max ₹500 as ceiling

    score = (
        weights["bio"]  * bio_norm  +
        weights["rec"]  * rec_norm  +
        weights["co2"]  * co2_norm  +
        weights["cost"] * cost_norm
    ) * 100
    return round(score, 2)


def _reasoning(query, mat, cost_inr, co2):
    parts = []
    if mat["bio"] >= 90:
        parts.append("highly biodegradable ({}%)".format(mat["bio"]))
    if mat["rec"] >= 90:
        parts.append("excellent recyclability ({}%)".format(mat["rec"]))
    if co2 < 0.6:
        parts.append("low CO2 footprint ({} kg)".format(co2))
    if cost_inr < 166:
        parts.append("cost-efficient (Rs.{}/unit)".format(cost_inr))
    if query.fragility_level == "high" and "Corrugated" in mat["material_type"]:
        parts.append("strong structural protection for fragile items")
    if query.moisture_sensitivity == "high" and "Film" in mat["material_type"]:
        parts.append("moisture-resistant barrier for sensitive products")
    return "Best choice because: " + (", ".join(parts) if parts else "good overall balance") + "."


def get_recommendation(query: QueryInput) -> RecommendationPayload:
    scored = []
    for mat in MATERIALS:
        features  = _build_features(query, mat)
        cost_inr  = _predict_cost_inr(features, mat)
        co2       = _predict_co2(features, mat)
        score     = _suitability_score(query, mat, cost_inr, co2)
        scored.append({
            "material_type":          mat["material_type"],
            "cost_per_unit_inr":      cost_inr,
            "co2_score":              co2,
            "biodegradability_score": mat["bio"],
            "recyclability_pct":      mat["rec"],
            "suitability_score":      score,
            "reasoning":              _reasoning(query, mat, cost_inr, co2),
        })

    scored.sort(key=lambda x: x["suitability_score"], reverse=True)
    recommendations = [RecommendationOut(rank=i + 1, **r) for i, r in enumerate(scored[:5])]

    top = recommendations[0]
    summary = (
        "For your {} product '{}', ".format(query.product_category, query.product_name) +
        "{} is the top recommendation with a suitability score of ".format(top.material_type) +
        "{}/100, cost of Rs.{}/unit, CO2 footprint of {} kg, ".format(top.suitability_score, top.cost_per_unit_inr, top.co2_score) +
        "and biodegradability of {}%.".format(top.biodegradability_score)
    )

    return RecommendationPayload(recommendations=recommendations, summary=summary)
