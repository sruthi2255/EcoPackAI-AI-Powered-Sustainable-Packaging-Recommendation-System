from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.database import SessionLocal, engine
from app import models
from app.schemas import QueryInput, RecommendationResponse, HistoryItem, StatsResponse
from app.recommender import get_recommendations

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EcoPackAI", version="2.0")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend(query: QueryInput, db: Session = Depends(get_db)):
    # Save query
    db_query = models.UserQuery(
        product_name=query.product_name,
        product_category=query.product_category,
        product_weight_kg=query.product_weight_kg,
        shipping_distance_km=query.shipping_distance_km,
        priority=query.priority,
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)

    # Get recommendations
    recs = get_recommendations(query)
    if not recs:
        raise HTTPException(status_code=422, detail="No suitable materials found for this product.")

    # Save results
    for rec in recs:
        db_result = models.RecommendationResult(
            query_id=db_query.id,
            rank=rec.rank,
            material_type=rec.material_type,
            co2_score=rec.co2_score,
            biodegradability_score=rec.biodegradability_score,
            recyclability_pct=rec.recyclability_pct,
            suitability_score=rec.suitability_score,
            reasoning=rec.reasoning,
        )
        db.add(db_result)
    db.commit()

    return RecommendationResponse(
        query_id=db_query.id,
        product_name=query.product_name,
        product_category=query.product_category,
        recommendations=recs,
    )


@app.get("/api/history", response_model=List[HistoryItem])
def history(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT uq.id AS query_id, uq.product_name, uq.product_category,
               uq.priority, rr.material_type AS top_material,
               rr.suitability_score AS top_score, uq.created_at
        FROM user_queries uq
        JOIN recommendation_results rr ON rr.query_id = uq.id AND rr.rank = 1
        ORDER BY uq.created_at DESC LIMIT 20
    """)).fetchall()
    return [HistoryItem(**dict(r._mapping)) for r in rows]


@app.get("/api/stats", response_model=List[StatsResponse])
def stats(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT uq.product_category AS category,
               COUNT(DISTINCT uq.id) AS total_queries,
               ROUND(AVG(rr.co2_score)::NUMERIC, 3) AS avg_co2,
               ROUND(AVG(rr.biodegradability_score)::NUMERIC, 1) AS avg_bio
        FROM user_queries uq
        JOIN recommendation_results rr ON rr.query_id = uq.id AND rr.rank = 1
        GROUP BY uq.product_category
        ORDER BY total_queries DESC
    """)).fetchall()
    return [StatsResponse(**dict(r._mapping)) for r in rows]