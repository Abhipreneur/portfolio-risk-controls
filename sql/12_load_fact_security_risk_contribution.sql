-- =========================================================
-- LOAD FACT SECURITY RISK CONTRIBUTION
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;

TRUNCATE TABLE
risk_platform.fact_security_risk_contribution;


CREATE TEMP TABLE staging_security_risk_contribution (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    ticker VARCHAR(30),

    portfolio_weight_pct NUMERIC(24, 12),

    standalone_annualized_volatility NUMERIC(24, 15),

    marginal_daily_risk NUMERIC(24, 15),

    component_daily_volatility NUMERIC(24, 15),

    component_annualized_volatility NUMERIC(24, 15),

    risk_contribution_pct NUMERIC(24, 12),

    security_id INTEGER,

    company_name VARCHAR(150),

    sector VARCHAR(100),

    risk_to_weight_ratio NUMERIC(24, 15),

    risk_contribution_rank INTEGER
);


-- Keep \copy on ONE line

\copy staging_security_risk_contribution FROM 'data/processed/security_risk_contribution.csv' WITH (FORMAT csv, HEADER true);


INSERT INTO risk_platform.fact_security_risk_contribution (

    valuation_date,
    portfolio_id,
    security_id,
    portfolio_weight_pct,
    standalone_annualized_volatility,
    marginal_daily_risk,
    component_daily_volatility,
    component_annualized_volatility,
    risk_contribution_pct,
    risk_to_weight_ratio,
    risk_contribution_rank

)

SELECT

    valuation_date,
    portfolio_id,
    security_id,
    portfolio_weight_pct,
    standalone_annualized_volatility,
    marginal_daily_risk,
    component_daily_volatility,
    component_annualized_volatility,
    risk_contribution_pct,
    risk_to_weight_ratio,
    risk_contribution_rank

FROM staging_security_risk_contribution;


COMMIT;