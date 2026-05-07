from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QueryInput(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200)
    product_category: str = Field(..., min_length=1, max_length=100)
    product_weight_kg: float = Field(..., gt=0)
    shipping_distance_km: float = Field(..., gt=0)
    priority: str = Field(..., pattern="^(eco|cost|balanced)$")


class RecommendationItem(BaseModel):
    rank: int
    material_type: str
    co2_score: float
    biodegradability_score: int
    recyclability_pct: int
    suitability_score: float
    reasoning: str

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    query_id: int
    product_name: str
    product_category: str
    recommendations: List[RecommendationItem]


class HistoryItem(BaseModel):
    query_id: int
    product_name: str
    product_category: str
    priority: str
    top_material: str
    top_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    category: str
    total_queries: int
    avg_co2: float
    avg_bio: float