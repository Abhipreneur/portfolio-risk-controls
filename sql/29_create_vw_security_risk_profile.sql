-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- POWER BI VIEW
-- SECURITY RISK PROFILE
-- =========================================================


CREATE OR REPLACE VIEW
risk_platform.vw_security_risk_profile
AS


SELECT

    -- -----------------------------------------------------
    -- IDENTIFIERS
    -- -----------------------------------------------------

    p.valuation_date,

    p.portfolio_id,

    p.security_id,

    s.ticker,

    s.company_name,

    s.sector,

    s.exchange,

    s.currency,


    -- -----------------------------------------------------
    -- POSITION / EXPOSURE
    -- -----------------------------------------------------

    p.quantity,

    p.market_price,

    p.market_value,

    p.target_value,

    p.target_weight_pct,

    p.actual_weight_pct,

    p.weight_difference_pct,

    p.allocation_difference,


    -- -----------------------------------------------------
    -- RISK CONTRIBUTION
    -- -----------------------------------------------------

    rc.standalone_annualized_volatility
        * 100
        AS standalone_volatility_pct,

    rc.risk_contribution_pct,

    rc.risk_to_weight_ratio,

    rc.component_annualized_volatility
        * 100
        AS component_volatility_pct,

    rc.risk_contribution_rank,


    -- -----------------------------------------------------
    -- LIQUIDITY
    -- -----------------------------------------------------

    l.adv_lookback_days,

    l.adv_shares,

    l.position_pct_adv,

    l.max_participation_rate,

    l.daily_liquidation_capacity,

    l.days_to_liquidate,

    l.liquidity_class,

    l.liquidity_rank


FROM risk_platform.fact_position p


JOIN risk_platform.dim_security s

    ON p.security_id =
       s.security_id


LEFT JOIN
risk_platform.fact_security_risk_contribution rc

    ON p.valuation_date =
       rc.valuation_date

    AND p.portfolio_id =
        rc.portfolio_id

    AND p.security_id =
        rc.security_id


LEFT JOIN
risk_platform.fact_liquidity l

    ON p.valuation_date =
       l.valuation_date

    AND p.portfolio_id =
        l.portfolio_id

    AND p.security_id =
        l.security_id;