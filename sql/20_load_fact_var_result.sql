-- =========================================================
-- LOAD FACT VAR RESULT
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE
risk_platform.fact_var_result;


-- ---------------------------------------------------------
-- STAGING TABLE MATCHES portfolio_var_summary.csv
-- ---------------------------------------------------------

CREATE TEMP TABLE staging_var_result (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    method VARCHAR(50),

    holding_period_days INTEGER,

    confidence_level NUMERIC(10, 6),

    historical_observations INTEGER,

    tail_observations INTEGER,

    var_pct NUMERIC(24, 15),

    var_amount NUMERIC(24, 6),

    expected_shortfall_pct NUMERIC(24, 15),

    expected_shortfall_amount NUMERIC(24, 6)
);


-- Keep \copy on ONE line

\copy staging_var_result FROM 'data/processed/portfolio_var_summary.csv' WITH (FORMAT csv, HEADER true);


INSERT INTO risk_platform.fact_var_result (

    valuation_date,
    portfolio_id,
    method,
    holding_period_days,
    confidence_level,
    historical_observations,
    tail_observations,
    var_pct,
    var_amount,
    expected_shortfall_pct,
    expected_shortfall_amount

)

SELECT

    valuation_date,
    portfolio_id,
    method,
    holding_period_days,
    confidence_level,
    historical_observations,
    tail_observations,
    var_pct,
    var_amount,
    expected_shortfall_pct,
    expected_shortfall_amount

FROM staging_var_result;


COMMIT;