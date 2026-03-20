from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

USD_TO_INR = 83.0  


class QueryInput(BaseModel):
    product_name: str                = Field(..., example="Smartphone")
    product_category: str            = Field(..., example="Electronics")
    product_weight_kg: float         = Field(..., gt=0, example=0.5)
    fragility_level: str             = Field(..., example="high")
    moisture_sensitivity: str        = Field(..., example="medium")
    shipping_distance_km: float      = Field(..., gt=0, example=500)
    budget_inr: Optional[float]      = Field(None, example=250.0)
    priority: str                    = Field(..., example="balanced")

    class Config:
        schema_extra = {
            "example": {
                "product_name": "Wireless Earbuds",
                "product_category": "Electronics",
                "product_weight_kg": 0.3,
                "fragility_level": "high",
                "moisture_sensitivity": "medium",
                "shipping_distance_km": 800,
                "budget_inr": 250.0,
                "priority": "eco"
            }
        }


class RecommendationOut(BaseModel):
    rank: int
    material_type: str
    cost_per_unit_inr: float
    co2_score: float
    biodegradability_score: int
    recyclability_pct: int
    suitability_score: float
    reasoning: str


class RecommendationPayload(BaseModel):
    recommendations: List[RecommendationOut]
    summary: str


class QueryResponse(RecommendationPayload):
    query_id: int
