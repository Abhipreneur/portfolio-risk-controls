-- =========================================================
-- LOAD FACT SECTOR RISK CONTRIBUTION
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE
risk_platform.fact_sector_risk_contribution;


-- ---------------------------------------------------------
-- STAGING TABLE MATCHES CSV EXACTLY
-- ---------------------------------------------------------

CREATE TEMP TABLE staging_sector_risk_contribution (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    risk_contribution_rank INTEGER,

    sector VARCHAR(100),

    security_count INTEGER,

    portfolio_weight_pct NUMERIC(24, 12),

    risk_contribution_pct NUMERIC(24, 12),

    risk_minus_weight_pct NUMERIC(24, 12),

    risk_to_weight_ratio NUMERIC(24, 15),

    component_annualized_volatility NUMERIC(24, 15)
);


-- Keep \copy on ONE line

\copy staging_sector_risk_contribution FROM 'data/processed/sector_risk_contribution.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- INSERT NORMALIZED FACT DATA
-- ---------------------------------------------------------

INSERT INTO risk_platform.fact_sector_risk_contribution (

    valuation_date,
    portfolio_id,
    sector,
    security_count,
    portfolio_weight_pct,
    risk_contribution_pct,
    risk_minus_weight_pct,
    risk_to_weight_ratio,
    component_annualized_volatility,
    risk_contribution_rank

)

SELECT

    valuation_date,
    portfolio_id,
    sector,
    security_count,
    portfolio_weight_pct,
    risk_contribution_pct,
    risk_minus_weight_pct,
    risk_to_weight_ratio,
    component_annualized_volatility,
    risk_contribution_rank

FROM staging_sector_risk_contribution;


COMMIT;