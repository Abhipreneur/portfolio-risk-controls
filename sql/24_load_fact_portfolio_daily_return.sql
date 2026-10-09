-- =========================================================
-- LOAD FACT PORTFOLIO DAILY RETURN
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE
risk_platform.fact_portfolio_daily_return;


CREATE TEMP TABLE staging_portfolio_daily_return (

    return_date DATE,

    portfolio_id VARCHAR(30),

    portfolio_return NUMERIC(24, 15),

    cumulative_growth NUMERIC(24, 15),

    cumulative_return NUMERIC(24, 15),

    running_peak NUMERIC(24, 15),

    drawdown NUMERIC(24, 15)
);


-- Keep \copy on ONE line

\copy staging_portfolio_daily_return FROM 'data/processed/portfolio_daily_returns.csv' WITH (FORMAT csv, HEADER true);


INSERT INTO risk_platform.fact_portfolio_daily_return (

    return_date,
    portfolio_id,
    portfolio_return,
    cumulative_growth,
    cumulative_return,
    running_peak,
    drawdown

)

SELECT

    return_date,
    portfolio_id,
    portfolio_return,
    cumulative_growth,
    cumulative_return,
    running_peak,
    drawdown

FROM staging_portfolio_daily_return;


COMMIT;