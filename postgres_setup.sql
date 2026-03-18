-- ============================================================
-- EcoPackAI – PostgreSQL Database Setup
-- Run this ONCE before starting the FastAPI server
-- ============================================================

-- STEP 1: Create the database (run as superuser)
CREATE DATABASE ecopackai_db;

-- STEP 2: Connect to it
\c ecopackai_db;

-- STEP 3: Create application user (optional but recommended)
CREATE USER ecopack_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ecopackai_db TO ecopack_user;
GRANT ALL ON SCHEMA public TO ecopack_user;

-- ============================================================
-- NOTE: Tables below are auto-created by SQLAlchemy on startup.
-- This section is for reference / manual inspection only.
-- ============================================================

-- Table: user_queries
-- Stores each recommendation request from the user
CREATE TABLE IF NOT EXISTS user_queries (
    id                   SERIAL PRIMARY KEY,
    product_name         VARCHAR(200) NOT NULL,
    product_category     VARCHAR(100) NOT NULL,
    product_weight_kg    FLOAT        NOT NULL,
    fragility_level      VARCHAR(20)  NOT NULL,  -- low / medium / high
    moisture_sensitivity VARCHAR(20)  NOT NULL,  -- low / medium / high
    shipping_distance_km FLOAT        NOT NULL,
    budget_usd           FLOAT,
    priority             VARCHAR(50)  NOT NULL,  -- eco / cost / balanced
    created_at           TIMESTAMPTZ  DEFAULT NOW()
);

-- Table: recommendation_results
-- Stores top-5 ranked material recommendations per query
CREATE TABLE IF NOT EXISTS recommendation_results (
    id                      SERIAL PRIMARY KEY,
    query_id                INTEGER REFERENCES user_queries(id) ON DELETE CASCADE,
    rank                    INTEGER      NOT NULL,  -- 1 = best
    material_type           VARCHAR(150) NOT NULL,
    cost_per_unit_usd       FLOAT        NOT NULL,
    co2_score               FLOAT        NOT NULL,
    biodegradability_score  INTEGER      NOT NULL,
    recyclability_pct       INTEGER      NOT NULL,
    suitability_score       FLOAT        NOT NULL,  -- 0-100 composite
    reasoning               TEXT,
    created_at              TIMESTAMPTZ  DEFAULT NOW()
);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_uq_category   ON user_queries(product_category);
CREATE INDEX IF NOT EXISTS idx_uq_created    ON user_queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rr_query_id   ON recommendation_results(query_id);
CREATE INDEX IF NOT EXISTS idx_rr_rank       ON recommendation_results(rank);

-- ============================================================
-- Verification queries
-- ============================================================

-- Check tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Preview queries
SELECT * FROM user_queries ORDER BY created_at DESC LIMIT 10;

-- Preview results with query info (JOIN)
SELECT
    uq.id        AS query_id,
    uq.product_name,
    uq.product_category,
    uq.priority,
    rr.rank,
    rr.material_type,
    rr.suitability_score,
    rr.co2_score,
    rr.cost_per_unit_usd
FROM user_queries uq
JOIN recommendation_results rr ON rr.query_id = uq.id
ORDER BY uq.created_at DESC, rr.rank ASC
LIMIT 30;

-- Sustainability summary (BI dashboard query)
SELECT
    uq.product_category,
    COUNT(DISTINCT uq.id)               AS total_queries,
    ROUND(AVG(rr.co2_score)::NUMERIC, 3)            AS avg_co2,
    ROUND(AVG(rr.biodegradability_score)::NUMERIC, 1) AS avg_bio,
    ROUND(AVG(rr.cost_per_unit_usd)::NUMERIC, 2)    AS avg_cost
FROM user_queries uq
JOIN recommendation_results rr ON rr.query_id = uq.id AND rr.rank = 1
GROUP BY uq.product_category
ORDER BY total_queries DESC;
