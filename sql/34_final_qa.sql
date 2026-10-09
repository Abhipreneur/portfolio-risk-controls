-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FINAL QA / RECONCILIATION
-- Snapshot: 2026-09-30
-- =========================================================


-- ---------------------------------------------------------
-- 1. CORE TABLE ROW COUNTS
-- ---------------------------------------------------------

SELECT
    dataset,
    actual_count,
    expected_count,
    CASE
        WHEN actual_count = expected_count THEN 'PASS'
        ELSE 'FAIL'
    END AS qa_status

FROM (

    SELECT
        'dim_security' AS dataset,
        COUNT(*) AS actual_count,
        25::bigint AS expected_count
    FROM risk_platform.dim_security

    UNION ALL

    SELECT
        'dim_portfolio',
        COUNT(*),
        1
    FROM risk_platform.dim_portfolio

    UNION ALL

    SELECT
        'dim_risk_limit',
        COUNT(*),
        8
    FROM risk_platform.dim_risk_limit

    UNION ALL

    SELECT
        'fact_position',
        COUNT(*),
        25
    FROM risk_platform.fact_position

    UNION ALL

    SELECT
        'fact_control_result',
        COUNT(*),
        66
    FROM risk_platform.fact_control_result

    UNION ALL

    SELECT
        'fact_control_exception',
        COUNT(*),
        6
    FROM risk_platform.fact_control_exception

    UNION ALL

    SELECT
        'fact_liquidity',
        COUNT(*),
        25
    FROM risk_platform.fact_liquidity

    UNION ALL

    SELECT
        'fact_security_risk_contribution',
        COUNT(*),
        25
    FROM risk_platform.fact_security_risk_contribution

    UNION ALL

    SELECT
        'fact_sector_risk_contribution',
        COUNT(*),
        11
    FROM risk_platform.fact_sector_risk_contribution

    UNION ALL

    SELECT
        'fact_stress_result',
        COUNT(*),
        4
    FROM risk_platform.fact_stress_result

    UNION ALL

    SELECT
        'fact_portfolio_risk_summary',
        COUNT(*),
        1
    FROM risk_platform.fact_portfolio_risk_summary

    UNION ALL

    SELECT
        'fact_var_result',
        COUNT(*),
        2
    FROM risk_platform.fact_var_result

    UNION ALL

    SELECT
        'fact_benchmark_risk_summary',
        COUNT(*),
        1
    FROM risk_platform.fact_benchmark_risk_summary

    UNION ALL

    SELECT
        'fact_portfolio_daily_return',
        COUNT(*),
        743
    FROM risk_platform.fact_portfolio_daily_return

    UNION ALL

    SELECT
        'fact_benchmark_daily_return',
        COUNT(*),
        738
    FROM risk_platform.fact_benchmark_daily_return

) q

ORDER BY dataset;


-- ---------------------------------------------------------
-- 2. CONTROL STATUS RECONCILIATION
-- ---------------------------------------------------------

SELECT
    status,
    COUNT(*) AS control_tests
FROM risk_platform.fact_control_result
GROUP BY status
ORDER BY status;


-- ---------------------------------------------------------
-- 3. EXECUTIVE KPI RECONCILIATION
-- ---------------------------------------------------------

SELECT
    valuation_date,
    portfolio_id,

    ROUND(target_aum, 2)
        AS target_aum,

    ROUND(invested_value, 2)
        AS invested_value,

    ROUND(annualized_volatility_pct, 4)
        AS annualized_volatility_pct,

    ROUND(historical_var_99_pct, 4)
        AS historical_var_99_pct,

    ROUND(historical_es_99_pct, 4)
        AS historical_es_99_pct,

    ROUND(beta, 4)
        AS beta,

    ROUND(worst_stress_loss_pct, 4)
        AS worst_stress_loss_pct,

    amber_control_tests,

    red_control_tests,

    open_exceptions

FROM risk_platform.vw_executive_risk_overview;


-- ---------------------------------------------------------
-- 4. RISK CONTRIBUTION RECONCILIATION
-- ---------------------------------------------------------

SELECT
    ROUND(
        SUM(risk_contribution_pct),
        6
    ) AS total_security_risk_contribution_pct

FROM risk_platform.fact_security_risk_contribution;


SELECT
    ROUND(
        SUM(risk_contribution_pct),
        6
    ) AS total_sector_risk_contribution_pct

FROM risk_platform.fact_sector_risk_contribution;


-- ---------------------------------------------------------
-- 5. POWER BI VIEW CHECK
-- ---------------------------------------------------------

SELECT
    table_name
FROM information_schema.views
WHERE table_schema = 'risk_platform'
AND table_name IN (
    'vw_executive_risk_overview',
    'vw_security_risk_profile',
    'vw_sector_risk_profile',
    'vw_controls_exceptions',
    'vw_stress_scenarios',
    'vw_portfolio_benchmark_timeseries'
)
ORDER BY table_name;