-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- CORE DATABASE SCHEMA
-- =========================================================


-- ---------------------------------------------------------
-- CREATE PROJECT SCHEMA
-- ---------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS risk_platform;


-- ---------------------------------------------------------
-- DIMENSION: SECURITY
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS risk_platform.dim_security (
    security_id INTEGER PRIMARY KEY,
    ticker VARCHAR(30) NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    exchange VARCHAR(30) NOT NULL,
    currency VARCHAR(10) NOT NULL
);


-- ---------------------------------------------------------
-- DIMENSION: PORTFOLIO
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS risk_platform.dim_portfolio (
    portfolio_id VARCHAR(30) PRIMARY KEY,
    portfolio_name VARCHAR(150) NOT NULL,
    base_currency VARCHAR(10) NOT NULL,
    target_aum NUMERIC(20, 2) NOT NULL,

    CONSTRAINT chk_target_aum_positive
        CHECK (target_aum > 0)
);


-- ---------------------------------------------------------
-- DIMENSION: RISK LIMIT
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS risk_platform.dim_risk_limit (
    control_id VARCHAR(30) PRIMARY KEY,
    control_name VARCHAR(150) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    warning_threshold NUMERIC(18, 6) NOT NULL,
    critical_threshold NUMERIC(18, 6) NOT NULL,
    unit VARCHAR(30) NOT NULL,

    CONSTRAINT chk_risk_limit_thresholds
        CHECK (
            critical_threshold
            >= warning_threshold
        )
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON SCHEMA risk_platform IS
'Institutional Portfolio Risk and Controls Platform';

COMMENT ON TABLE risk_platform.dim_security IS
'Reference master for securities held or analyzed in the portfolio.';

COMMENT ON TABLE risk_platform.dim_portfolio IS
'Portfolio-level reference information including target AUM and base currency.';

COMMENT ON TABLE risk_platform.dim_risk_limit IS
'Configured warning and critical thresholds used by the automated risk control engine.';