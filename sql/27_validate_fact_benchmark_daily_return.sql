-- =========================================================
-- VALIDATE FACT BENCHMARK DAILY RETURN
-- =========================================================


-- ---------------------------------------------------------
-- 1. RETURN SERIES RECONCILIATION
-- ---------------------------------------------------------

SELECT
    portfolio_id,
    benchmark,
    COUNT(*) AS observations,
    MIN(return_date) AS start_date,
    MAX(return_date) AS end_date,

    ROUND(
        CORR(
            portfolio_return,
            benchmark_return
        )::numeric,
        4
    ) AS correlation,

    ROUND(
        (
            STDDEV_SAMP(active_return)
            * SQRT(252::numeric)
            * 100
        )::numeric,
        4
    ) AS tracking_error_pct

FROM risk_platform.fact_benchmark_daily_return

GROUP BY
    portfolio_id,
    benchmark;


-- ---------------------------------------------------------
-- 2. LATEST CUMULATIVE RETURNS
-- ---------------------------------------------------------

SELECT
    return_date,
    portfolio_id,
    benchmark,

    ROUND(
        (portfolio_growth - 1) * 100,
        4
    ) AS portfolio_cumulative_return_pct,

    ROUND(
        (benchmark_growth - 1) * 100,
        4
    ) AS benchmark_cumulative_return_pct

FROM risk_platform.fact_benchmark_daily_return

ORDER BY return_date DESC

LIMIT 1;