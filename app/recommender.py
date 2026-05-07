"""
EcoPackAI – Recommender Engine
Category-specific material pools, no cost/fragility/moisture outputs.
"""
import os
import numpy as np
from typing import List, Dict
from app.schemas import QueryInput, RecommendationItem
import joblib
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# ──────────────────────────────────────────────
# CATEGORY-SPECIFIC MATERIAL POOLS
# Each material: co2 (kg), bio (0-100), rec (0-100), weight_limit_kg
# ──────────────────────────────────────────────
CATEGORY_MATERIALS: Dict[str, List[Dict]] = {
    "Electronics": [
        {"name": "Molded Pulp Tray",        "co2": 0.35, "bio": 85, "rec": 78, "weight_limit": 10},
        {"name": "EPE Foam Insert",          "co2": 1.20, "bio": 10, "rec": 30, "weight_limit": 50},
        {"name": "Corrugated Double-Wall",   "co2": 0.45, "bio": 80, "rec": 90, "weight_limit": 25},
        {"name": "Air Column Cushioning",    "co2": 0.55, "bio": 20, "rec": 60, "weight_limit": 15},
        {"name": "Honeycomb Cardboard",      "co2": 0.30, "bio": 88, "rec": 92, "weight_limit": 20},
        {"name": "Anti-Static Bubble Wrap",  "co2": 0.90, "bio": 15, "rec": 40, "weight_limit": 30},
        {"name": "rPET Blister Pack",        "co2": 0.60, "bio": 25, "rec": 80, "weight_limit": 5},
    ],
    "Food & Beverage": [
        {"name": "Kraft Paper Wrap",         "co2": 0.20, "bio": 95, "rec": 85, "weight_limit": 5},
        {"name": "Biodegradable PLA Film",   "co2": 0.40, "bio": 90, "rec": 50, "weight_limit": 3},
        {"name": "Sugarcane Bagasse Box",    "co2": 0.15, "bio": 98, "rec": 70, "weight_limit": 8},
        {"name": "Beeswax-Coated Paper",     "co2": 0.18, "bio": 92, "rec": 55, "weight_limit": 2},
        {"name": "Mushroom Packaging",       "co2": 0.10, "bio": 99, "rec": 60, "weight_limit": 4},
        {"name": "Corrugated Tray Insert",   "co2": 0.38, "bio": 82, "rec": 88, "weight_limit": 10},
        {"name": "Recycled Paperboard",      "co2": 0.28, "bio": 78, "rec": 92, "weight_limit": 6},
    ],
    "Clothing & Apparel": [
        {"name": "Recycled Tissue Paper",    "co2": 0.12, "bio": 90, "rec": 88, "weight_limit": 2},
        {"name": "Cotton Muslin Bag",        "co2": 0.22, "bio": 95, "rec": 70, "weight_limit": 3},
        {"name": "Kraft Mailer Box",         "co2": 0.30, "bio": 85, "rec": 90, "weight_limit": 5},
        {"name": "rPET Poly Mailer",         "co2": 0.50, "bio": 20, "rec": 75, "weight_limit": 4},
        {"name": "Seaweed Foam Sheet",       "co2": 0.08, "bio": 99, "rec": 65, "weight_limit": 1},
        {"name": "Compostable Mailer",       "co2": 0.18, "bio": 96, "rec": 55, "weight_limit": 3},
        {"name": "Recycled Cardboard Box",   "co2": 0.35, "bio": 80, "rec": 92, "weight_limit": 8},
    ],
    "Furniture & Wood": [
        {"name": "Corrugated Double-Wall",   "co2": 0.45, "bio": 80, "rec": 90, "weight_limit": 80},
        {"name": "Honeycomb Kraft Board",    "co2": 0.30, "bio": 88, "rec": 92, "weight_limit": 60},
        {"name": "Stretch Film (rPET)",      "co2": 0.65, "bio": 20, "rec": 70, "weight_limit": 200},
        {"name": "Foam Edge Protectors",     "co2": 1.00, "bio": 15, "rec": 35, "weight_limit": 100},
        {"name": "Recycled Cardboard Shell", "co2": 0.40, "bio": 82, "rec": 90, "weight_limit": 50},
        {"name": "Wooden Crate",             "co2": 0.55, "bio": 70, "rec": 60, "weight_limit": 300},
        {"name": "Biodeg. Kraft Corner Pad", "co2": 0.22, "bio": 90, "rec": 85, "weight_limit": 40},
    ],
    "Cosmetics & Beauty": [
        {"name": "Recycled Glass Wrap",      "co2": 0.28, "bio": 75, "rec": 90, "weight_limit": 3},
        {"name": "Seed Paper Filler",        "co2": 0.10, "bio": 99, "rec": 80, "weight_limit": 1},
        {"name": "Kraft Tissue Paper",       "co2": 0.15, "bio": 95, "rec": 88, "weight_limit": 2},
        {"name": "Biodeg. Foam Cushion",     "co2": 0.35, "bio": 88, "rec": 55, "weight_limit": 5},
        {"name": "Compostable Shrink Wrap",  "co2": 0.20, "bio": 93, "rec": 50, "weight_limit": 2},
        {"name": "Molded Pulp Insert",       "co2": 0.32, "bio": 87, "rec": 80, "weight_limit": 4},
        {"name": "rPET Clamshell Box",       "co2": 0.55, "bio": 22, "rec": 78, "weight_limit": 3},
    ],
    "Pharmaceuticals": [
        {"name": "Blister PVC/Alu Pack",     "co2": 0.80, "bio": 10, "rec": 40, "weight_limit": 1},
        {"name": "Recycled Paperboard Box",  "co2": 0.28, "bio": 82, "rec": 92, "weight_limit": 3},
        {"name": "Biodeg. Cold Pack",        "co2": 0.45, "bio": 80, "rec": 60, "weight_limit": 5},
        {"name": "Kraft Padded Mailer",      "co2": 0.25, "bio": 88, "rec": 85, "weight_limit": 4},
        {"name": "Insulated Pulp Box",       "co2": 0.38, "bio": 85, "rec": 78, "weight_limit": 6},
        {"name": "Compostable Bubble Mailer","co2": 0.30, "bio": 92, "rec": 58, "weight_limit": 3},
        {"name": "HDPE Vial Tray",           "co2": 0.70, "bio": 12, "rec": 65, "weight_limit": 2},
    ],
    "Toys & Games": [
        {"name": "Molded Pulp Tray",         "co2": 0.35, "bio": 85, "rec": 78, "weight_limit": 5},
        {"name": "Corrugated Display Box",   "co2": 0.42, "bio": 82, "rec": 90, "weight_limit": 15},
        {"name": "Recycled Cardboard Box",   "co2": 0.38, "bio": 80, "rec": 92, "weight_limit": 10},
        {"name": "Honeycomb Insert",         "co2": 0.28, "bio": 88, "rec": 92, "weight_limit": 8},
        {"name": "Biodeg. Foam Sheet",       "co2": 0.50, "bio": 75, "rec": 50, "weight_limit": 6},
        {"name": "Mushroom Packaging",       "co2": 0.10, "bio": 99, "rec": 60, "weight_limit": 4},
        {"name": "rPET Poly Bag",            "co2": 0.55, "bio": 18, "rec": 72, "weight_limit": 3},
    ],
    "Industrial & Hardware": [
        {"name": "Heavy-Duty Corrugated",    "co2": 0.55, "bio": 78, "rec": 88, "weight_limit": 100},
        {"name": "Wooden Pallet + Film",     "co2": 0.80, "bio": 65, "rec": 55, "weight_limit": 500},
        {"name": "VCI Poly Bag",             "co2": 0.70, "bio": 12, "rec": 50, "weight_limit": 50},
        {"name": "Foam Corner Protectors",   "co2": 1.10, "bio": 10, "rec": 30, "weight_limit": 80},
        {"name": "Stretch Wrap (rPET)",      "co2": 0.65, "bio": 18, "rec": 70, "weight_limit": 300},
        {"name": "Steel Strapping Band",     "co2": 1.50, "bio": 5,  "rec": 90, "weight_limit": 1000},
        {"name": "Honeycomb Pallet Wrap",    "co2": 0.35, "bio": 85, "rec": 90, "weight_limit": 120},
    ],
    "Books & Stationery": [
        {"name": "Kraft Mailer",             "co2": 0.18, "bio": 92, "rec": 90, "weight_limit": 3},
        {"name": "Recycled Bubble Mailer",   "co2": 0.30, "bio": 40, "rec": 65, "weight_limit": 2},
        {"name": "Corrugated Book Wrap",     "co2": 0.35, "bio": 82, "rec": 90, "weight_limit": 5},
        {"name": "Compostable Poly Mailer",  "co2": 0.20, "bio": 94, "rec": 55, "weight_limit": 2},
        {"name": "Seed Paper Wrapper",       "co2": 0.10, "bio": 99, "rec": 80, "weight_limit": 1},
        {"name": "Recycled Cardboard Box",   "co2": 0.38, "bio": 80, "rec": 92, "weight_limit": 8},
        {"name": "Honeycomb Paper Wrap",     "co2": 0.22, "bio": 90, "rec": 92, "weight_limit": 4},
    ],
    # Default fallback for any other category
    "General": [
        {"name": "Corrugated Cardboard",     "co2": 0.45, "bio": 80, "rec": 90, "weight_limit": 30},
        {"name": "Biodeg. Foam",             "co2": 0.60, "bio": 85, "rec": 50, "weight_limit": 20},
        {"name": "Kraft Paper Wrap",         "co2": 0.20, "bio": 95, "rec": 85, "weight_limit": 10},
        {"name": "Mushroom Packaging",       "co2": 0.10, "bio": 99, "rec": 60, "weight_limit": 8},
        {"name": "PLA Film",                 "co2": 0.40, "bio": 90, "rec": 50, "weight_limit": 5},
        {"name": "rPET Poly Mailer",         "co2": 0.50, "bio": 20, "rec": 75, "weight_limit": 4},
        {"name": "Honeycomb Cardboard",      "co2": 0.30, "bio": 88, "rec": 92, "weight_limit": 25},
    ],
}


def _get_materials_for_category(category: str) -> List[Dict]:
    """Return the material pool for the given category, fallback to General."""
    # Normalize: try direct match, then fuzzy
    if category in CATEGORY_MATERIALS:
        return CATEGORY_MATERIALS[category]
    for key in CATEGORY_MATERIALS:
        if key.lower() in category.lower() or category.lower() in key.lower():
            return CATEGORY_MATERIALS[key]
    return CATEGORY_MATERIALS["General"]


def _distance_factor(km: float) -> float:
    """Higher distance = higher co2 multiplier."""
    if km <= 100:
        return 1.0
    elif km <= 500:
        return 1.15
    elif km <= 1000:
        return 1.30
    elif km <= 3000:
        return 1.50
    else:
        return 1.75


def _weight_factor(weight_kg: float, weight_limit: float) -> float:
    """Penalise materials that are borderline for the product weight."""
    ratio = weight_kg / max(weight_limit, 0.1)
    if ratio > 1.0:
        return 0.0   # cannot support this weight
    elif ratio > 0.8:
        return 0.6
    elif ratio > 0.5:
        return 0.85
    return 1.0


def _score_material(material: Dict, query: QueryInput, dist_factor: float) -> float:
    """Compute a 0-100 suitability score for a material."""
    wf = _weight_factor(query.product_weight_kg, material["weight_limit"])
    if wf == 0.0:
        return 0.0

    co2_adjusted = material["co2"] * dist_factor
    # Normalise co2: assume max realistic = 2.0 kg → lower is better
    co2_norm = max(0, 1 - co2_adjusted / 2.0)

    bio_norm = material["bio"] / 100
    rec_norm = material["rec"] / 100

    if query.priority == "eco":
        weights = {"co2": 0.45, "bio": 0.35, "rec": 0.20}
    elif query.priority == "cost":
        # cost-priority: still eco metrics but favour recyclability (proxy for mainstream)
        weights = {"co2": 0.20, "bio": 0.20, "rec": 0.60}
    else:  # balanced
        weights = {"co2": 0.35, "bio": 0.35, "rec": 0.30}

    base = (
        weights["co2"] * co2_norm +
        weights["bio"] * bio_norm +
        weights["rec"] * rec_norm
    ) * 100

    return round(base * wf, 2)


def _build_reasoning(material: Dict, query: QueryInput, score: float, rank: int) -> str:
    dist_factor = _distance_factor(query.shipping_distance_km)
    co2_adj = round(material["co2"] * dist_factor, 3)
    wf = _weight_factor(query.product_weight_kg, material["weight_limit"])

    lines = []
    if rank == 1:
        lines.append(f"Top pick for {query.product_category} products.")
    bio = material["bio"]
    rec = material["rec"]
    if bio >= 90:
        lines.append("Highly biodegradable — excellent end-of-life profile.")
    elif bio >= 70:
        lines.append("Good biodegradability score.")
    else:
        lines.append("Lower biodegradability — consider end-of-life disposal plan.")

    if rec >= 85:
        lines.append(f"Widely recyclable ({rec}%).")
    elif rec >= 60:
        lines.append(f"Moderately recyclable ({rec}%).")
    else:
        lines.append(f"Limited recyclability ({rec}%) — offset by other eco benefits.")

    lines.append(
        f"Estimated CO₂ footprint {co2_adj} kg for {query.shipping_distance_km} km shipping."
    )
    if wf < 1.0:
        lines.append(
            f"Note: product weight ({query.product_weight_kg} kg) is near this material's limit — "
            "verify structural integrity."
        )
    lines.append(f"Suitability score: {score}/100 under '{query.priority}' optimisation.")
    return " ".join(lines)


def get_recommendations(query: QueryInput) -> List[RecommendationItem]:
    """Return top-5 ranked RecommendationItems for the given query."""
    materials = _get_materials_for_category(query.product_category)
    dist_factor = _distance_factor(query.shipping_distance_km)

    scored = []
    for mat in materials:
        score = _score_material(mat, query, dist_factor)
        if score > 0:
            scored.append((score, mat))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)
    top5 = scored[:5]

    results = []
    for rank, (score, mat) in enumerate(top5, start=1):
        co2_adj = round(mat["co2"] * dist_factor, 3)
        reasoning = _build_reasoning(mat, query, score, rank)
        results.append(RecommendationItem(
            rank=rank,
            material_type=mat["name"],
            co2_score=co2_adj,
            biodegradability_score=mat["bio"],
            recyclability_pct=mat["rec"],
            suitability_score=score,
            reasoning=reasoning,
        ))
    return results