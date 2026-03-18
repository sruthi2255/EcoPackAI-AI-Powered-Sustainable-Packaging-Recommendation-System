from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class UserQuery(Base):
    __tablename__ = "user_queries"

    id                   = Column(Integer, primary_key=True, index=True)
    product_name         = Column(String(200), nullable=False)
    product_category     = Column(String(100), nullable=False)
    product_weight_kg    = Column(Float, nullable=False)
    fragility_level      = Column(String(20), nullable=False)
    moisture_sensitivity = Column(String(20), nullable=False)
    shipping_distance_km = Column(Float, nullable=False)
    budget_inr           = Column(Float, nullable=True)
    priority             = Column(String(50), nullable=False)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())

    recommendations = relationship("RecommendationResult", back_populates="query")


class RecommendationResult(Base):
    __tablename__ = "recommendation_results"

    id                     = Column(Integer, primary_key=True, index=True)
    query_id               = Column(Integer, ForeignKey("user_queries.id"), nullable=False)
    rank                   = Column(Integer, nullable=False)
    material_type          = Column(String(150), nullable=False)
    cost_per_unit_inr      = Column(Float, nullable=False)
    co2_score              = Column(Float, nullable=False)
    biodegradability_score = Column(Integer, nullable=False)
    recyclability_pct      = Column(Integer, nullable=False)
    suitability_score      = Column(Float, nullable=False)
    reasoning              = Column(Text, nullable=True)
    created_at             = Column(DateTime(timezone=True), server_default=func.now())

    query = relationship("UserQuery", back_populates="recommendations")
