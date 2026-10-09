-- =========================================================
-- LOAD FACT BENCHMARK DAILY RETURN
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE
risk_platform.fact_benchmark_daily_return;


CREATE TEMP TABLE staging_benchmark_daily_return (

    return_date DATE,

    portfolio_id VARCHAR(30),

    benchmark VARCHAR(100),

    portfolio_return NUMERIC(24, 15),

    benchmark_return NUMERIC(24, 15),

    active_return NUMERIC(24, 15),

    portfolio_growth NUMERIC(24, 15),

    benchmark_growth NUMERIC(24, 15)
);


-- Keep \copy on ONE line

\copy staging_benchmark_daily_return FROM 'data/processed/portfolio_benchmark_returns.csv' WITH (FORMAT csv, HEADER true);


INSERT INTO risk_platform.fact_benchmark_daily_return (

    return_date,
    portfolio_id,
    benchmark,
    portfolio_return,
    benchmark_return,
    active_return,
    portfolio_growth,
    benchmark_growth

)

SELECT

    return_date,
    portfolio_id,
    benchmark,
    portfolio_return,
    benchmark_return,
    active_return,
    portfolio_growth,
    benchmark_growth

FROM staging_benchmark_daily_return;


COMMIT;