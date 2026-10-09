-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT PORTFOLIO DAILY RETURN
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_portfolio_daily_return (

    return_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    portfolio_return NUMERIC(24, 15) NOT NULL,

    cumulative_growth NUMERIC(24, 15) NOT NULL,

    cumulative_return NUMERIC(24, 15) NOT NULL,

    running_peak NUMERIC(24, 15) NOT NULL,

    drawdown NUMERIC(24, 15) NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_portfolio_daily_return
        PRIMARY KEY (
            return_date,
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEY
    -- -----------------------------------------------------

    CONSTRAINT fk_portfolio_daily_return_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_daily_cumulative_growth
        CHECK (
            cumulative_growth > 0
        ),

    CONSTRAINT chk_daily_running_peak
        CHECK (
            running_peak > 0
        ),

    CONSTRAINT chk_daily_peak_vs_growth
        CHECK (
            running_peak >= cumulative_growth
        ),

    CONSTRAINT chk_daily_drawdown
        CHECK (
            drawdown <= 0
        ),


    -- cumulative_return = cumulative_growth - 1

    CONSTRAINT chk_daily_cumulative_return_reconciliation
        CHECK (
            ABS(
                cumulative_return
                - (cumulative_growth - 1)
            ) <= 0.000000000001
        ),


    -- drawdown = cumulative_growth / running_peak - 1

    CONSTRAINT chk_daily_drawdown_reconciliation
        CHECK (
            ABS(
                drawdown
                -
                (
                    cumulative_growth
                    / running_peak
                    - 1
                )
            ) <= 0.000000000001
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_portfolio_daily_return_portfolio
ON risk_platform.fact_portfolio_daily_return (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_portfolio_daily_return_date
ON risk_platform.fact_portfolio_daily_return (
    return_date
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_portfolio_daily_return IS
'Daily historical simulated portfolio returns, cumulative growth and drawdown using current portfolio weights.';


COMMENT ON COLUMN risk_platform.fact_portfolio_daily_return.portfolio_return IS
'Daily simulated portfolio return based on current portfolio weights applied to historical security returns.';


COMMENT ON COLUMN risk_platform.fact_portfolio_daily_return.drawdown IS
'Percentage decline from the historical running peak, expressed as a decimal fraction.';