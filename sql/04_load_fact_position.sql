-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- LOAD FACT POSITION
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


-- ---------------------------------------------------------
-- CLEAR EXISTING POSITION DATA
-- ---------------------------------------------------------

TRUNCATE TABLE risk_platform.fact_position;


-- ---------------------------------------------------------
-- CREATE TEMPORARY STAGING TABLE
--
-- This matches the CSV exactly, including descriptive
-- fields that will NOT be stored in fact_position.
-- ---------------------------------------------------------

CREATE TEMP TABLE staging_initial_positions (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    security_id INTEGER,

    ticker VARCHAR(30),

    company_name VARCHAR(150),

    sector VARCHAR(100),

    target_weight_pct NUMERIC(18, 10),

    actual_weight_pct NUMERIC(18, 10),

    weight_difference_pct NUMERIC(18, 10),

    target_value NUMERIC(20, 2),

    quantity BIGINT,

    market_price NUMERIC(20, 10),

    market_value NUMERIC(20, 2),

    allocation_difference NUMERIC(20, 2)
);


-- ---------------------------------------------------------
-- LOAD CSV INTO STAGING TABLE
--
-- IMPORTANT:
-- \copy must remain on ONE LINE.
-- ---------------------------------------------------------

\copy staging_initial_positions FROM 'data/processed/initial_positions.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- INSERT NORMALIZED DATA INTO FACT TABLE
-- ---------------------------------------------------------

INSERT INTO risk_platform.fact_position (

    valuation_date,
    portfolio_id,
    security_id,
    target_weight_pct,
    actual_weight_pct,
    weight_difference_pct,
    target_value,
    quantity,
    market_price,
    market_value,
    allocation_difference

)

SELECT

    valuation_date,
    portfolio_id,
    security_id,
    target_weight_pct,
    actual_weight_pct,
    weight_difference_pct,
    target_value,
    quantity,
    market_price,
    market_value,
    allocation_difference

FROM staging_initial_positions;


COMMIT;