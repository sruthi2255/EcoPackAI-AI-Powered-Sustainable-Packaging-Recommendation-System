from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import uvicorn

from .database import engine, get_db, Base
from .models import UserQuery, RecommendationResult
from .schemas import QueryInput, QueryResponse, RecommendationOut
from .recommender import get_recommendation

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EcoPackAI",
    description="AI-Powered Sustainable Packaging Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/recommend", response_model=QueryResponse)
async def recommend(query: QueryInput, db: Session = Depends(get_db)):
    result = get_recommendation(query)

    db_query = UserQuery(
        product_name=query.product_name,
        product_category=query.product_category,
        product_weight_kg=query.product_weight_kg,
        fragility_level=query.fragility_level,
        moisture_sensitivity=query.moisture_sensitivity,
        shipping_distance_km=query.shipping_distance_km,
        budget_inr=query.budget_inr,
        priority=query.priority,
    )
    db.add(db_query)
    db.flush()

    for rec in result.recommendations:
        db_rec = RecommendationResult(
            query_id=db_query.id,
            material_type=rec.material_type,
            rank=rec.rank,
            cost_per_unit_inr=rec.cost_per_unit_inr,
            co2_score=rec.co2_score,
            biodegradability_score=rec.biodegradability_score,
            recyclability_pct=rec.recyclability_pct,
            suitability_score=rec.suitability_score,
            reasoning=rec.reasoning,
        )
        db.add(db_rec)

    db.commit()
    db.refresh(db_query)
    return QueryResponse(query_id=db_query.id, **result.dict())


@app.get("/api/history")
async def get_history(limit: int = 20, db: Session = Depends(get_db)):
    queries = db.query(UserQuery).order_by(UserQuery.created_at.desc()).limit(limit).all()
    history = []
    for q in queries:
        top = (
            db.query(RecommendationResult)
            .filter(RecommendationResult.query_id == q.id, RecommendationResult.rank == 1)
            .first()
        )
        history.append({
            "id": q.id,
            "product_name": q.product_name,
            "product_category": q.product_category,
            "created_at": str(q.created_at),
            "top_material": top.material_type if top else "N/A",
            "top_score": round(top.suitability_score, 2) if top else 0,
            "top_cost_inr": top.cost_per_unit_inr if top else 0,
        })
    return history


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_queries = db.query(UserQuery).count()
    total_recs    = db.query(RecommendationResult).count()
    avg_co2 = db.query(func.avg(RecommendationResult.co2_score))\
                .filter(RecommendationResult.rank == 1).scalar() or 0
    avg_bio = db.query(func.avg(RecommendationResult.biodegradability_score))\
                .filter(RecommendationResult.rank == 1).scalar() or 0
    avg_cost_inr = db.query(func.avg(RecommendationResult.cost_per_unit_inr))\
                .filter(RecommendationResult.rank == 1).scalar() or 0
    return {
        "total_queries": total_queries,
        "total_recommendations": total_recs,
        "avg_co2_top_picks": round(float(avg_co2), 2),
        "avg_biodegradability": round(float(avg_bio), 2),
        "avg_cost_inr": round(float(avg_cost_inr), 2),
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
