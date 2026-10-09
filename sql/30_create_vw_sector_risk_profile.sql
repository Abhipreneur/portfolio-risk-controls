-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- POWER BI VIEW
-- SECTOR RISK PROFILE
-- =========================================================


CREATE OR REPLACE VIEW
risk_platform.vw_sector_risk_profile
AS


SELECT

    -- -----------------------------------------------------
    -- IDENTIFIERS
    -- -----------------------------------------------------

    sr.valuation_date,

    sr.portfolio_id,

    dp.portfolio_name,

    sr.sector,


    -- -----------------------------------------------------
    -- SECTOR EXPOSURE
    -- -----------------------------------------------------

    sr.security_count,

    sr.portfolio_weight_pct,


    -- -----------------------------------------------------
    -- RISK CONTRIBUTION
    -- -----------------------------------------------------

    sr.risk_contribution_pct,

    sr.risk_minus_weight_pct,

    sr.risk_to_weight_ratio,

    sr.component_annualized_volatility
        * 100
        AS component_volatility_pct,

    sr.risk_contribution_rank,


    -- -----------------------------------------------------
    -- SECTOR CONCENTRATION CONTROL
    -- -----------------------------------------------------

    cr.metric_value
        AS concentration_metric_pct,

    cr.warning_threshold,

    cr.critical_threshold,

    cr.status
        AS concentration_status


FROM
risk_platform.fact_sector_risk_contribution sr


JOIN risk_platform.dim_portfolio dp

    ON sr.portfolio_id =
       dp.portfolio_id


LEFT JOIN risk_platform.fact_control_result cr

    ON sr.valuation_date =
       cr.valuation_date

    AND sr.portfolio_id =
        cr.portfolio_id

    AND cr.control_id =
        'RISK002'

    AND cr.entity_type =
        'Sector'

    AND cr.entity_name =
        sr.sector;