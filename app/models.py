from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserQuery(Base):
    __tablename__ = "user_queries"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(200), nullable=False)
    product_category = Column(String(100), nullable=False)
    product_weight_kg = Column(Float, nullable=False)
    shipping_distance_km = Column(Float, nullable=False)
    priority = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    results = relationship("RecommendationResult", back_populates="query", cascade="all, delete")


class RecommendationResult(Base):
    __tablename__ = "recommendation_results"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("user_queries.id", ondelete="CASCADE"))
    rank = Column(Integer, nullable=False)
    material_type = Column(String(150), nullable=False)
    co2_score = Column(Float, nullable=False)
    biodegradability_score = Column(Integer, nullable=False)
    recyclability_pct = Column(Integer, nullable=False)
    suitability_score = Column(Float, nullable=False)
    reasoning = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    query = relationship("UserQuery", back_populates="results")