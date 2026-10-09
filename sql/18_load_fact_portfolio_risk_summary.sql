-- =========================================================
-- LOAD FACT PORTFOLIO RISK SUMMARY
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE
risk_platform.fact_portfolio_risk_summary;


CREATE TEMP TABLE staging_portfolio_risk_summary (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    return_observations INTEGER,

    average_daily_return NUMERIC(24, 15),

    daily_volatility NUMERIC(24, 15),

    annualized_volatility NUMERIC(24, 15),

    cumulative_return NUMERIC(24, 15),

    maximum_drawdown NUMERIC(24, 15),

    max_drawdown_date DATE,

    best_daily_return NUMERIC(24, 15),

    worst_daily_return NUMERIC(24, 15)
);


-- Keep \copy on ONE line

\copy staging_portfolio_risk_summary FROM 'data/processed/portfolio_risk_summary.csv' WITH (FORMAT csv, HEADER true);


INSERT INTO risk_platform.fact_portfolio_risk_summary (

    valuation_date,
    portfolio_id,
    return_observations,
    average_daily_return,
    daily_volatility,
    annualized_volatility,
    cumulative_return,
    maximum_drawdown,
    max_drawdown_date,
    best_daily_return,
    worst_daily_return

)

SELECT

    valuation_date,
    portfolio_id,
    return_observations,
    average_daily_return,
    daily_volatility,
    annualized_volatility,
    cumulative_return,
    maximum_drawdown,
    max_drawdown_date,
    best_daily_return,
    worst_daily_return

FROM staging_portfolio_risk_summary;


COMMIT;