-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- POWER BI VIEW
-- EXECUTIVE RISK OVERVIEW
-- =========================================================


CREATE OR REPLACE VIEW
risk_platform.vw_executive_risk_overview
AS


-- ---------------------------------------------------------
-- POSITION / AUM SUMMARY
-- ---------------------------------------------------------

WITH position_summary AS (

    SELECT
        p.valuation_date,
        p.portfolio_id,

        COUNT(*) AS security_count,

        SUM(
            p.market_value
        ) AS invested_value,

        SUM(
            p.actual_weight_pct
        ) AS equity_weight_pct,

        MAX(
            p.actual_weight_pct
        ) AS largest_security_weight_pct

    FROM risk_platform.fact_position p

    GROUP BY
        p.valuation_date,
        p.portfolio_id
),


-- ---------------------------------------------------------
-- LIQUIDITY SUMMARY
-- ---------------------------------------------------------

liquidity_summary AS (

    SELECT
        valuation_date,
        portfolio_id,

        MAX(
            days_to_liquidate
        ) AS max_days_to_liquidate,

        AVG(
            days_to_liquidate
        ) AS avg_days_to_liquidate

    FROM risk_platform.fact_liquidity

    GROUP BY
        valuation_date,
        portfolio_id
),


-- ---------------------------------------------------------
-- CONTROL STATUS SUMMARY
-- ---------------------------------------------------------

control_summary AS (

    SELECT
        valuation_date,
        portfolio_id,

        COUNT(*) AS total_control_tests,

        COUNT(*) FILTER (
            WHERE status = 'GREEN'
        ) AS green_control_tests,

        COUNT(*) FILTER (
            WHERE status = 'AMBER'
        ) AS amber_control_tests,

        COUNT(*) FILTER (
            WHERE status = 'RED'
        ) AS red_control_tests

    FROM risk_platform.fact_control_result

    GROUP BY
        valuation_date,
        portfolio_id
),


-- ---------------------------------------------------------
-- EXCEPTION SUMMARY
-- ---------------------------------------------------------

exception_summary AS (

    SELECT
        cr.valuation_date,
        cr.portfolio_id,

        COUNT(*) FILTER (
            WHERE ce.exception_status = 'OPEN'
        ) AS open_exceptions,

        COUNT(*) FILTER (
            WHERE ce.exception_status = 'UNDER_REVIEW'
        ) AS under_review_exceptions,

        COUNT(*) FILTER (
            WHERE ce.exception_status = 'CLOSED'
        ) AS closed_exceptions,

        COUNT(*) FILTER (
            WHERE ce.exception_status = 'WAIVED'
        ) AS waived_exceptions

    FROM risk_platform.fact_control_exception ce

    JOIN risk_platform.fact_control_result cr
        ON ce.control_result_id =
           cr.control_result_id

    GROUP BY
        cr.valuation_date,
        cr.portfolio_id
),


-- ---------------------------------------------------------
-- 99% HISTORICAL VAR / EXPECTED SHORTFALL
-- ---------------------------------------------------------

var_99 AS (

    SELECT
        valuation_date,
        portfolio_id,

        var_pct,
        var_amount,

        expected_shortfall_pct,
        expected_shortfall_amount

    FROM risk_platform.fact_var_result

    WHERE method = 'Historical'

      AND confidence_level = 0.99

      AND holding_period_days = 1
),


-- ---------------------------------------------------------
-- WORST STRESS SCENARIO
-- ---------------------------------------------------------

worst_stress AS (

    SELECT DISTINCT ON (
        valuation_date,
        portfolio_id
    )

        valuation_date,
        portfolio_id,

        scenario_id,
        scenario_name,

        stress_loss_amount,
        portfolio_loss_pct

    FROM risk_platform.fact_stress_result

    ORDER BY
        valuation_date,
        portfolio_id,
        stress_severity_rank
)


-- ---------------------------------------------------------
-- FINAL EXECUTIVE VIEW
-- ---------------------------------------------------------

SELECT

    ps.valuation_date,

    ps.portfolio_id,

    dp.portfolio_name,

    dp.base_currency,

    dp.target_aum,


    -- Portfolio composition

    ps.security_count,

    ps.invested_value,

    (
        dp.target_aum
        - ps.invested_value
    ) AS residual_cash,

    ps.equity_weight_pct,

    ps.largest_security_weight_pct,


    -- Portfolio risk

    prs.annualized_volatility
        * 100
        AS annualized_volatility_pct,

    prs.maximum_drawdown
        * 100
        AS maximum_drawdown_pct,


    -- VaR / Expected Shortfall

    v.var_pct
        * 100
        AS historical_var_99_pct,

    v.var_amount
        AS historical_var_99_amount,

    v.expected_shortfall_pct
        * 100
        AS historical_es_99_pct,

    v.expected_shortfall_amount
        AS historical_es_99_amount,


    -- Benchmark analytics

    br.benchmark,

    br.beta,

    br.correlation,

    br.r_squared,

    br.annualized_tracking_error
        * 100
        AS tracking_error_pct,

    br.information_ratio,


    -- Stress testing

    ws.scenario_id
        AS worst_stress_scenario_id,

    ws.scenario_name
        AS worst_stress_scenario,

    ws.portfolio_loss_pct
        AS worst_stress_loss_pct,

    ws.stress_loss_amount
        AS worst_stress_loss_amount,


    -- Liquidity

    ls.max_days_to_liquidate,

    ls.avg_days_to_liquidate,


    -- Controls

    cs.total_control_tests,

    cs.green_control_tests,

    cs.amber_control_tests,

    cs.red_control_tests,


    -- Exceptions

    COALESCE(
        es.open_exceptions,
        0
    ) AS open_exceptions,

    COALESCE(
        es.under_review_exceptions,
        0
    ) AS under_review_exceptions,

    COALESCE(
        es.closed_exceptions,
        0
    ) AS closed_exceptions,

    COALESCE(
        es.waived_exceptions,
        0
    ) AS waived_exceptions


FROM position_summary ps


JOIN risk_platform.dim_portfolio dp
    ON ps.portfolio_id =
       dp.portfolio_id


JOIN risk_platform.fact_portfolio_risk_summary prs
    ON ps.valuation_date =
       prs.valuation_date

    AND ps.portfolio_id =
        prs.portfolio_id


LEFT JOIN var_99 v
    ON ps.valuation_date =
       v.valuation_date

    AND ps.portfolio_id =
        v.portfolio_id


LEFT JOIN risk_platform.fact_benchmark_risk_summary br
    ON ps.valuation_date =
       br.valuation_date

    AND ps.portfolio_id =
        br.portfolio_id


LEFT JOIN worst_stress ws
    ON ps.valuation_date =
       ws.valuation_date

    AND ps.portfolio_id =
        ws.portfolio_id


LEFT JOIN liquidity_summary ls
    ON ps.valuation_date =
       ls.valuation_date

    AND ps.portfolio_id =
        ls.portfolio_id


LEFT JOIN control_summary cs
    ON ps.valuation_date =
       cs.valuation_date

    AND ps.portfolio_id =
        cs.portfolio_id


LEFT JOIN exception_summary es
    ON ps.valuation_date =
       es.valuation_date

    AND ps.portfolio_id =
        es.portfolio_id;