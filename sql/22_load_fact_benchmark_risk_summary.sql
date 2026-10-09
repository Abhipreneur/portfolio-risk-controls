-- =========================================================
-- LOAD FACT BENCHMARK RISK SUMMARY
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE
risk_platform.fact_benchmark_risk_summary;


CREATE TEMP TABLE staging_benchmark_risk_summary (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    benchmark VARCHAR(100),

    aligned_return_observations INTEGER,

    start_date DATE,

    end_date DATE,

    beta NUMERIC(24, 15),

    correlation NUMERIC(24, 15),

    r_squared NUMERIC(24, 15),

    portfolio_annualized_volatility NUMERIC(24, 15),

    benchmark_annualized_volatility NUMERIC(24, 15),

    annualized_tracking_error NUMERIC(24, 15),

    annualized_active_return NUMERIC(24, 15),

    information_ratio NUMERIC(24, 15),

    portfolio_cumulative_return NUMERIC(24, 15),

    benchmark_cumulative_return NUMERIC(24, 15)
);


-- Keep \copy on ONE line

\copy staging_benchmark_risk_summary FROM 'data/processed/benchmark_risk_summary.csv' WITH (FORMAT csv, HEADER true);


INSERT INTO risk_platform.fact_benchmark_risk_summary (

    valuation_date,
    portfolio_id,
    benchmark,
    aligned_return_observations,
    start_date,
    end_date,
    beta,
    correlation,
    r_squared,
    portfolio_annualized_volatility,
    benchmark_annualized_volatility,
    annualized_tracking_error,
    annualized_active_return,
    information_ratio,
    portfolio_cumulative_return,
    benchmark_cumulative_return

)

SELECT

    valuation_date,
    portfolio_id,
    benchmark,
    aligned_return_observations,
    start_date,
    end_date,
    beta,
    correlation,
    r_squared,
    portfolio_annualized_volatility,
    benchmark_annualized_volatility,
    annualized_tracking_error,
    annualized_active_return,
    information_ratio,
    portfolio_cumulative_return,
    benchmark_cumulative_return

FROM staging_benchmark_risk_summary;


COMMIT;