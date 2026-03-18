"""
run.py — Start the entire EcoPackAI project with one command.

Usage:
    python run.py

This script:
1. Loads your .env file (DATABASE_URL)
2. Tests the PostgreSQL connection
3. Creates all database tables automatically
4. Starts the FastAPI server on http://localhost:8000
"""

import os
import sys
from dotenv import load_dotenv

# ── Step 1: Load environment variables from .env ─────────────────────────────
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    print("Open .env and set: DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ecopackai_db")
    sys.exit(1)

print("✓ .env loaded")
print(f"✓ Database: {DATABASE_URL.split('@')[-1]}")  # print only host part, hide password

# ── Step 2: Test PostgreSQL connection ────────────────────────────────────────
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✓ PostgreSQL connection successful")
except Exception as e:
    print(f"\nERROR: Cannot connect to PostgreSQL")
    print(f"Reason: {e}")
    print("\nMake sure:")
    print("  1. PostgreSQL is running (check Services in Windows)")
    print("  2. Your password in .env is correct")
    print("  3. The database 'ecopackai_db' exists in pgAdmin")
    sys.exit(1)

# ── Step 3: Create all tables ─────────────────────────────────────────────────
try:
    from app.database import Base, engine as app_engine
    from app.models import UserQuery, RecommendationResult
    Base.metadata.create_all(bind=app_engine)
    print("✓ Database tables created (user_queries, recommendation_results)")
except Exception as e:
    print(f"ERROR creating tables: {e}")
    sys.exit(1)

# ── Step 4: Start FastAPI server ──────────────────────────────────────────────
print("\n" + "="*50)
print("  EcoPackAI is starting...")
print("="*50)
print("  UI:       http://localhost:8000")
print("  API Docs: http://localhost:8000/docs")
print("  Stop:     Ctrl + C")
print("="*50 + "\n")

import uvicorn
if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)