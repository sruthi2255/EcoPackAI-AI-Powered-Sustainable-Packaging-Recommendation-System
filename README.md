# EcoPackAI – Setup & Model Integration Guide

## Project Structure
```
ecopackai/
├── app/
│   ├── __init__.py
│   ├── main.py          ← FastAPI app + routes
│   ├── database.py      ← PostgreSQL connection (SQLAlchemy)
│   ├── models.py        ← ORM table definitions
│   ├── schemas.py       ← Pydantic request/response models
│   └── recommender.py  ← ⭐ YOUR MODEL PLUGS IN HERE
├── models/              ← Drop your .pkl files here
├── templates/
│   └── index.html       ← Frontend UI
├── postgres_setup.sql   ← DB setup reference
└── requirements.txt
```

---

## STEP 1 — PostgreSQL Setup

```bash
# Install PostgreSQL (Ubuntu)
sudo apt install postgresql postgresql-contrib

# Start service
sudo service postgresql start

# Create database
sudo -u postgres psql -f postgres_setup.sql
```

Or in the psql shell:
```sql
CREATE DATABASE ecopackai_db;
\c ecopackai_db
-- Tables are auto-created by SQLAlchemy on first run
```

---

## STEP 2 — Configure Connection

Edit `app/database.py` or set this environment variable:

```bash
export DATABASE_URL="postgresql://postgres:your_password@localhost:5432/ecopackai_db"
```

Or create a `.env` file:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ecopackai_db
```

---

## STEP 3 — Install Dependencies

```bash
cd ecopackai
pip install -r requirements.txt
```

---

## STEP 4 — Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open browser: http://localhost:8000
API docs:     http://localhost:8000/docs

---

## ⭐ STEP 5 — Connect YOUR Trained Model

### 5a. Save your models after training (run in your notebook):

```python
import joblib

# Save Random Forest (cost predictor)
joblib.dump(rf_model, "models/rf_cost_model.pkl")

# Save XGBoost (CO2 predictor)
joblib.dump(xgb_model, "models/xgb_co2_model.pkl")

# Save preprocessing objects
joblib.dump(label_encoder, "models/label_encoder.pkl")
joblib.dump(scaler,        "models/scaler.pkl")
```

### 5b. Load models in `app/recommender.py`:

Uncomment these lines at the top of recommender.py:

```python
rf_model      = joblib.load(os.path.join(MODEL_DIR, "rf_cost_model.pkl"))
xgb_model     = joblib.load(os.path.join(MODEL_DIR, "xgb_co2_model.pkl"))
label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
scaler        = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
```

### 5c. Replace `_build_features()` to match your training feature order:

```python
def _build_features(query: QueryInput, material: dict) -> np.ndarray:
    # Match EXACTLY the columns you used during training
    category_enc = label_encoder.transform([query.product_category])[0]
    features = [
        query.product_weight_kg,
        _encode_level(query.fragility_level),
        _encode_level(query.moisture_sensitivity),
        query.shipping_distance_km,
        query.budget_usd or 0,
        category_enc,
        material["base_cost"],
        material["co2"],
        material["bio"],
        material["rec"],
    ]
    return scaler.transform([features])
```

### 5d. Replace `_predict_cost()` and `_predict_co2()`:

```python
def _predict_cost(features, material):
    return float(rf_model.predict(features)[0])

def _predict_co2(features, material):
    return float(xgb_model.predict(features)[0])
```

That's it — the scoring, ranking, DB storage, and UI all work automatically!

---

## API Endpoints

| Method | Endpoint          | Description                          |
|--------|-------------------|--------------------------------------|
| GET    | /                 | Frontend UI                          |
| POST   | /api/recommend    | Run AI recommendation (stores to DB) |
| GET    | /api/history      | Last 20 queries with top result      |
| GET    | /api/stats        | Aggregate stats for dashboard        |
| GET    | /docs             | Swagger / OpenAPI interactive docs   |

---

## PostgreSQL Tables

**user_queries** — one row per user request
```
id | product_name | product_category | product_weight_kg | fragility_level |
moisture_sensitivity | shipping_distance_km | budget_usd | priority | created_at
```

**recommendation_results** — 5 rows per query (rank 1–5)
```
id | query_id (FK) | rank | material_type | cost_per_unit_usd |
co2_score | biodegradability_score | recyclability_pct |
suitability_score | reasoning | created_at
```
