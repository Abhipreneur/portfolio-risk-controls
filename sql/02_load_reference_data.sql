-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- LOAD REFERENCE DATA
-- =========================================================

\set ON_ERROR_STOP on


-- ---------------------------------------------------------
-- START TRANSACTION
-- ---------------------------------------------------------

BEGIN;


-- ---------------------------------------------------------
-- CLEAR EXISTING REFERENCE DATA
-- ---------------------------------------------------------

TRUNCATE TABLE risk_platform.dim_security;
TRUNCATE TABLE risk_platform.dim_portfolio;
TRUNCATE TABLE risk_platform.dim_risk_limit;


-- ---------------------------------------------------------
-- LOAD SECURITY MASTER
-- IMPORTANT: \copy command must stay on ONE line
-- ---------------------------------------------------------

\copy risk_platform.dim_security (security_id, ticker, company_name, sector, exchange, currency) FROM 'data/reference/dim_security.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- LOAD PORTFOLIO MASTER
-- ---------------------------------------------------------

\copy risk_platform.dim_portfolio (portfolio_id, portfolio_name, base_currency, target_aum) FROM 'data/reference/portfolio_master.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- LOAD RISK LIMITS
-- ---------------------------------------------------------

\copy risk_platform.dim_risk_limit (control_id, control_name, metric_name, warning_threshold, critical_threshold, unit) FROM 'data/reference/risk_limits.csv' WITH (FORMAT csv, HEADER true);


-- ---------------------------------------------------------
-- COMMIT
-- ---------------------------------------------------------

COMMIT;