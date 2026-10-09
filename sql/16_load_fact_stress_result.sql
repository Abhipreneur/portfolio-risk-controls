-- =========================================================
-- LOAD FACT STRESS RESULT
-- =========================================================

\set ON_ERROR_STOP on

BEGIN;


TRUNCATE TABLE risk_platform.fact_stress_result;


-- ---------------------------------------------------------
-- STAGING TABLE MATCHES stress_test_summary.csv EXACTLY
-- ---------------------------------------------------------

CREATE TEMP TABLE staging_stress_results (

    valuation_date DATE,

    portfolio_id VARCHAR(30),

    scenario_id VARCHAR(30),

    scenario_name VARCHAR(150),

    starting_portfolio_value NUMERIC(24, 6),

    starting_equity_value NUMERIC(24, 6),

    residual_cash NUMERIC(24, 6),

    stressed_equity_value NUMERIC(24, 6),

    stressed_portfolio_value NUMERIC(24, 6),

    stress_pnl NUMERIC(24, 6),

    stress_loss_amount NUMERIC(24, 6),

    portfolio_loss_pct NUMERIC(24, 12),

    largest_loss_contributor VARCHAR(30),

    largest_loss_contribution_amount NUMERIC(24, 6),

    largest_loss_contribution_pct NUMERIC(24, 12),

    stress_severity_rank INTEGER
);


-- Keep \copy on ONE line

\copy staging_stress_results FROM 'data/processed/stress_test_summary.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- INSERT NORMALIZED STRESS RESULTS
--
-- Map largest-loss ticker to security_id.
-- ---------------------------------------------------------

INSERT INTO risk_platform.fact_stress_result (

    valuation_date,
    portfolio_id,
    scenario_id,
    scenario_name,
    starting_portfolio_value,
    starting_equity_value,
    residual_cash,
    stressed_equity_value,
    stressed_portfolio_value,
    stress_pnl,
    stress_loss_amount,
    portfolio_loss_pct,
    largest_loss_security_id,
    largest_loss_contribution_amount,
    largest_loss_contribution_pct,
    stress_severity_rank

)

SELECT

    st.valuation_date,
    st.portfolio_id,
    st.scenario_id,
    st.scenario_name,
    st.starting_portfolio_value,
    st.starting_equity_value,
    st.residual_cash,
    st.stressed_equity_value,
    st.stressed_portfolio_value,
    st.stress_pnl,
    st.stress_loss_amount,
    st.portfolio_loss_pct,
    s.security_id,
    st.largest_loss_contribution_amount,
    st.largest_loss_contribution_pct,
    st.stress_severity_rank

FROM staging_stress_results st

JOIN risk_platform.dim_security s
    ON st.largest_loss_contributor = s.ticker;


COMMIT;