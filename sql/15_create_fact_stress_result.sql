-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT STRESS RESULT
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_stress_result (

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    scenario_id VARCHAR(30) NOT NULL,

    scenario_name VARCHAR(150) NOT NULL,

    starting_portfolio_value NUMERIC(24, 6) NOT NULL,

    starting_equity_value NUMERIC(24, 6) NOT NULL,

    residual_cash NUMERIC(24, 6) NOT NULL,

    stressed_equity_value NUMERIC(24, 6) NOT NULL,

    stressed_portfolio_value NUMERIC(24, 6) NOT NULL,

    stress_pnl NUMERIC(24, 6) NOT NULL,

    stress_loss_amount NUMERIC(24, 6) NOT NULL,

    portfolio_loss_pct NUMERIC(24, 12) NOT NULL,

    largest_loss_security_id INTEGER NOT NULL,

    largest_loss_contribution_amount NUMERIC(24, 6) NOT NULL,

    largest_loss_contribution_pct NUMERIC(24, 12) NOT NULL,

    stress_severity_rank INTEGER NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_fact_stress_result
        PRIMARY KEY (
            valuation_date,
            portfolio_id,
            scenario_id
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEYS
    -- -----------------------------------------------------

    CONSTRAINT fk_stress_result_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),

    CONSTRAINT fk_stress_result_security
        FOREIGN KEY (
            largest_loss_security_id
        )
        REFERENCES risk_platform.dim_security (
            security_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_stress_starting_portfolio
        CHECK (
            starting_portfolio_value > 0
        ),

    CONSTRAINT chk_stress_starting_equity
        CHECK (
            starting_equity_value >= 0
        ),

    CONSTRAINT chk_stress_residual_cash
        CHECK (
            residual_cash >= 0
        ),

    CONSTRAINT chk_stress_stressed_equity
        CHECK (
            stressed_equity_value >= 0
        ),

    CONSTRAINT chk_stress_stressed_portfolio
        CHECK (
            stressed_portfolio_value >= 0
        ),

    CONSTRAINT chk_stress_loss_amount
        CHECK (
            stress_loss_amount >= 0
        ),

    CONSTRAINT chk_stress_portfolio_loss_pct
        CHECK (
            portfolio_loss_pct >= 0
        ),

    CONSTRAINT chk_stress_largest_contribution
        CHECK (
            largest_loss_contribution_amount >= 0
            AND largest_loss_contribution_pct >= 0
        ),

    CONSTRAINT chk_stress_rank
        CHECK (
            stress_severity_rank > 0
        ),


    -- -----------------------------------------------------
    -- PORTFOLIO VALUE RECONCILIATION
    --
    -- starting portfolio =
    -- starting equity + cash
    -- -----------------------------------------------------

    CONSTRAINT chk_stress_start_value_reconciliation
        CHECK (
            ABS(
                starting_portfolio_value
                -
                (
                    starting_equity_value
                    + residual_cash
                )
            ) <= 0.01
        ),


    -- -----------------------------------------------------
    -- STRESSED VALUE RECONCILIATION
    -- -----------------------------------------------------

    CONSTRAINT chk_stress_end_value_reconciliation
        CHECK (
            ABS(
                stressed_portfolio_value
                -
                (
                    stressed_equity_value
                    + residual_cash
                )
            ) <= 0.01
        ),


    -- -----------------------------------------------------
    -- P&L RECONCILIATION
    -- -----------------------------------------------------

    CONSTRAINT chk_stress_pnl_reconciliation
        CHECK (
            ABS(
                stress_pnl
                -
                (
                    stressed_portfolio_value
                    - starting_portfolio_value
                )
            ) <= 0.01
        ),


    -- -----------------------------------------------------
    -- CURRENT SCENARIOS ARE DOWNSIDE STRESSES,
    -- THEREFORE LOSS AMOUNT = - STRESS P&L
    -- -----------------------------------------------------

    CONSTRAINT chk_stress_loss_reconciliation
        CHECK (
            ABS(
                stress_loss_amount
                + stress_pnl
            ) <= 0.01
        ),


    -- -----------------------------------------------------
    -- LOSS % RECONCILIATION
    -- -----------------------------------------------------

    CONSTRAINT chk_stress_loss_pct_reconciliation
        CHECK (
            ABS(
                portfolio_loss_pct
                -
                (
                    stress_loss_amount
                    / starting_portfolio_value
                    * 100
                )
            ) <= 0.000001
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_stress_result_portfolio
ON risk_platform.fact_stress_result (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_stress_result_scenario
ON risk_platform.fact_stress_result (
    scenario_id
);


CREATE INDEX IF NOT EXISTS idx_stress_result_rank
ON risk_platform.fact_stress_result (
    stress_severity_rank
);


CREATE INDEX IF NOT EXISTS idx_stress_result_loss
ON risk_platform.fact_stress_result (
    portfolio_loss_pct
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_stress_result IS
'Portfolio-level downside stress-test results by scenario and valuation date.';


COMMENT ON COLUMN risk_platform.fact_stress_result.portfolio_loss_pct IS
'Stress loss as a percentage of starting portfolio value.';


COMMENT ON COLUMN risk_platform.fact_stress_result.largest_loss_security_id IS
'Security contributing the largest absolute loss within the stress scenario.';