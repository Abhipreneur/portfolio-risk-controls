-- =========================================================
-- LOAD FACT CONTROL RESULTS
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE risk_platform.fact_control_result
RESTART IDENTITY;


-- ---------------------------------------------------------
-- STAGING TABLE MATCHES CSV EXACTLY
-- ---------------------------------------------------------

CREATE TEMP TABLE staging_control_results (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    control_id VARCHAR(30),

    control_name VARCHAR(150),

    entity_type VARCHAR(30),

    entity_name VARCHAR(150),

    metric_name VARCHAR(100),

    metric_value NUMERIC(24, 12),

    warning_threshold NUMERIC(18, 6),

    critical_threshold NUMERIC(18, 6),

    unit VARCHAR(30),

    status VARCHAR(10),

    exception_description TEXT
);


-- \copy MUST remain on one line

\copy staging_control_results FROM 'data/processed/control_results.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- LOAD NORMALIZED FACT TABLE
-- ---------------------------------------------------------

INSERT INTO risk_platform.fact_control_result (

    valuation_date,
    portfolio_id,
    control_id,
    entity_type,
    entity_name,
    metric_value,
    warning_threshold,
    critical_threshold,
    status,
    exception_description

)

SELECT

    valuation_date,
    portfolio_id,
    control_id,
    entity_type,
    entity_name,
    metric_value,
    warning_threshold,
    critical_threshold,
    status,
    exception_description

FROM staging_control_results;


COMMIT;