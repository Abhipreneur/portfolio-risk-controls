-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- LOAD FACT LIQUIDITY
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


-- ---------------------------------------------------------
-- CLEAR EXISTING DATA
-- ---------------------------------------------------------

TRUNCATE TABLE risk_platform.fact_liquidity;


-- ---------------------------------------------------------
-- STAGING TABLE MATCHES liquidity_risk.csv EXACTLY
-- ---------------------------------------------------------

CREATE TEMP TABLE staging_liquidity (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    security_id INTEGER,

    ticker VARCHAR(30),

    company_name VARCHAR(150),

    sector VARCHAR(100),

    quantity NUMERIC(24, 6),

    market_value NUMERIC(24, 6),

    adv_lookback_days INTEGER,

    adv_shares NUMERIC(24, 6),

    position_pct_adv NUMERIC(24, 12),

    max_participation_rate NUMERIC(18, 10),

    daily_liquidation_capacity NUMERIC(24, 6),

    days_to_liquidate NUMERIC(24, 12),

    liquidity_class VARCHAR(20),

    liquidity_rank INTEGER
);


-- IMPORTANT: keep \copy on ONE line

\copy staging_liquidity FROM 'data/processed/liquidity_risk.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- INSERT NORMALIZED DATA
-- ---------------------------------------------------------

INSERT INTO risk_platform.fact_liquidity (

    valuation_date,
    portfolio_id,
    security_id,
    adv_lookback_days,
    adv_shares,
    position_pct_adv,
    max_participation_rate,
    daily_liquidation_capacity,
    days_to_liquidate,
    liquidity_class,
    liquidity_rank

)

SELECT

    valuation_date,
    portfolio_id,
    security_id,
    adv_lookback_days,
    adv_shares,
    position_pct_adv,
    max_participation_rate,
    daily_liquidation_capacity,
    days_to_liquidate,
    liquidity_class,
    liquidity_rank

FROM staging_liquidity;


COMMIT;