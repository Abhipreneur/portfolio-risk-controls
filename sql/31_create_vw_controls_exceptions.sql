-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- POWER BI VIEW
-- CONTROLS & EXCEPTIONS
-- =========================================================


CREATE OR REPLACE VIEW
risk_platform.vw_controls_exceptions
AS


SELECT

    -- -----------------------------------------------------
    -- IDENTIFIERS
    -- -----------------------------------------------------

    cr.control_result_id,

    cr.valuation_date,

    cr.portfolio_id,

    dp.portfolio_name,

    cr.control_id,

    rl.control_name,

    rl.metric_name,

    rl.unit,


    -- -----------------------------------------------------
    -- CONTROL ENTITY
    -- -----------------------------------------------------

    cr.entity_type,

    cr.entity_name,


    -- -----------------------------------------------------
    -- CONTROL VALUES
    -- -----------------------------------------------------

    cr.metric_value,

    cr.warning_threshold,

    cr.critical_threshold,

    cr.status,


    -- -----------------------------------------------------
    -- STATUS SORTING FOR POWER BI
    -- -----------------------------------------------------

    CASE

        WHEN cr.status = 'RED'
            THEN 3

        WHEN cr.status = 'AMBER'
            THEN 2

        WHEN cr.status = 'GREEN'
            THEN 1

        ELSE 0

    END AS status_rank,


    -- -----------------------------------------------------
    -- THRESHOLD UTILIZATION
    --
    -- Example:
    -- metric 24 / critical threshold 25 = 96%
    -- -----------------------------------------------------

    CASE

        WHEN cr.critical_threshold > 0

        THEN
            (
                cr.metric_value
                / cr.critical_threshold
                * 100
            )

        ELSE NULL

    END AS critical_threshold_utilization_pct,


    -- -----------------------------------------------------
    -- DISTANCE TO CRITICAL THRESHOLD
    --
    -- Positive = still below critical
    -- Negative = critical threshold exceeded
    -- -----------------------------------------------------

    (
        cr.critical_threshold
        - cr.metric_value
    ) AS distance_to_critical_threshold,


    -- -----------------------------------------------------
    -- EXCEPTION FLAG
    -- -----------------------------------------------------

    CASE

        WHEN ce.exception_id IS NOT NULL
            THEN 1

        ELSE 0

    END AS has_exception,


    -- -----------------------------------------------------
    -- EXCEPTION DETAILS
    -- -----------------------------------------------------

    ce.exception_id,

    ce.exception_status,

    COALESCE(
        ce.exception_description,
        cr.exception_description
    ) AS exception_description


FROM risk_platform.fact_control_result cr


JOIN risk_platform.dim_risk_limit rl

    ON cr.control_id =
       rl.control_id


JOIN risk_platform.dim_portfolio dp

    ON cr.portfolio_id =
       dp.portfolio_id


LEFT JOIN risk_platform.fact_control_exception ce

    ON cr.control_result_id =
       ce.control_result_id;