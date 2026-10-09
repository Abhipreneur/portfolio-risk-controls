-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- LOAD FACT CONTROL EXCEPTIONS
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


-- ---------------------------------------------------------
-- CLEAR EXISTING EXCEPTIONS
-- ---------------------------------------------------------

TRUNCATE TABLE risk_platform.fact_control_exception;


-- ---------------------------------------------------------
-- STAGING TABLE MATCHES CSV EXACTLY
-- ---------------------------------------------------------

CREATE TEMP TABLE staging_control_exceptions (

    exception_id VARCHAR(30),

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

    exception_status VARCHAR(30),

    exception_description TEXT
);


-- IMPORTANT: keep \copy on ONE line

\copy staging_control_exceptions FROM 'data/processed/control_exceptions.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- MAP EXCEPTIONS TO CONTROL RESULTS
-- ---------------------------------------------------------

INSERT INTO risk_platform.fact_control_exception (

    exception_id,
    control_result_id,
    exception_status,
    exception_description

)

SELECT

    e.exception_id,
    r.control_result_id,
    e.exception_status,
    e.exception_description

FROM staging_control_exceptions e

JOIN risk_platform.fact_control_result r
    ON r.valuation_date = e.valuation_date
    AND r.portfolio_id = e.portfolio_id
    AND r.control_id = e.control_id
    AND r.entity_type = e.entity_type
    AND r.entity_name = e.entity_name;


COMMIT;