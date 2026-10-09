-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- POWER BI VIEW
-- STRESS SCENARIOS
-- =========================================================


CREATE OR REPLACE VIEW
risk_platform.vw_stress_scenarios
AS


SELECT

    -- -----------------------------------------------------
    -- IDENTIFIERS
    -- -----------------------------------------------------

    sr.valuation_date,

    sr.portfolio_id,

    dp.portfolio_name,

    sr.scenario_id,

    sr.scenario_name,

    sr.stress_severity_rank,


    -- -----------------------------------------------------
    -- STARTING PORTFOLIO
    -- -----------------------------------------------------

    sr.starting_portfolio_value,

    sr.starting_equity_value,

    sr.residual_cash,


    -- -----------------------------------------------------
    -- STRESSED PORTFOLIO
    -- -----------------------------------------------------

    sr.stressed_equity_value,

    sr.stressed_portfolio_value,

    sr.stress_pnl,

    sr.stress_loss_amount,

    sr.portfolio_loss_pct,


    -- -----------------------------------------------------
    -- LARGEST LOSS CONTRIBUTOR
    -- -----------------------------------------------------

    sr.largest_loss_security_id,

    s.ticker
        AS largest_loss_contributor,

    s.company_name
        AS largest_loss_company,

    s.sector
        AS largest_loss_sector,

    sr.largest_loss_contribution_amount,

    sr.largest_loss_contribution_pct,


    -- -----------------------------------------------------
    -- POWER BI FLAG
    -- -----------------------------------------------------

    CASE

        WHEN sr.stress_severity_rank = 1
            THEN 1

        ELSE 0

    END AS is_worst_scenario


FROM risk_platform.fact_stress_result sr


JOIN risk_platform.dim_portfolio dp

    ON sr.portfolio_id =
       dp.portfolio_id


JOIN risk_platform.dim_security s

    ON sr.largest_loss_security_id =
       s.security_id;