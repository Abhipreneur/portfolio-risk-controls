-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT PORTFOLIO RISK SUMMARY
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_portfolio_risk_summary (

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    return_observations INTEGER NOT NULL,

    average_daily_return NUMERIC(24, 15) NOT NULL,

    daily_volatility NUMERIC(24, 15) NOT NULL,

    annualized_volatility NUMERIC(24, 15) NOT NULL,

    cumulative_return NUMERIC(24, 15) NOT NULL,

    maximum_drawdown NUMERIC(24, 15) NOT NULL,

    max_drawdown_date DATE NOT NULL,

    best_daily_return NUMERIC(24, 15) NOT NULL,

    worst_daily_return NUMERIC(24, 15) NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_portfolio_risk_summary
        PRIMARY KEY (
            valuation_date,
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEY
    -- -----------------------------------------------------

    CONSTRAINT fk_portfolio_risk_summary_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_portfolio_risk_observations
        CHECK (
            return_observations > 0
        ),

    CONSTRAINT chk_portfolio_daily_volatility
        CHECK (
            daily_volatility >= 0
        ),

    CONSTRAINT chk_portfolio_annualized_volatility
        CHECK (
            annualized_volatility >= 0
        ),

    CONSTRAINT chk_portfolio_max_drawdown
        CHECK (
            maximum_drawdown <= 0
        ),

    CONSTRAINT chk_portfolio_best_worst_return
        CHECK (
            best_daily_return >= worst_daily_return
        ),

    CONSTRAINT chk_portfolio_drawdown_date
        CHECK (
            max_drawdown_date <= valuation_date
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_portfolio_risk_portfolio
ON risk_platform.fact_portfolio_risk_summary (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_portfolio_risk_date
ON risk_platform.fact_portfolio_risk_summary (
    valuation_date
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_portfolio_risk_summary IS
'Portfolio-level historical return and market-risk summary including volatility and maximum drawdown.';


COMMENT ON COLUMN risk_platform.fact_portfolio_risk_summary.maximum_drawdown IS
'Maximum historical simulated peak-to-trough decline using current portfolio weights.';


COMMENT ON COLUMN risk_platform.fact_portfolio_risk_summary.cumulative_return IS
'Historical simulated cumulative return using current portfolio weights; not realized portfolio performance.';