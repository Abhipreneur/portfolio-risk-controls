-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT VAR RESULT
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_var_result (

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    method VARCHAR(50) NOT NULL,

    holding_period_days INTEGER NOT NULL,

    confidence_level NUMERIC(10, 6) NOT NULL,

    historical_observations INTEGER NOT NULL,

    tail_observations INTEGER,

    var_pct NUMERIC(24, 15) NOT NULL,

    var_amount NUMERIC(24, 6) NOT NULL,

    expected_shortfall_pct NUMERIC(24, 15),

    expected_shortfall_amount NUMERIC(24, 6),


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_fact_var_result
        PRIMARY KEY (
            valuation_date,
            portfolio_id,
            method,
            holding_period_days,
            confidence_level
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEY
    -- -----------------------------------------------------

    CONSTRAINT fk_var_result_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_var_holding_period
        CHECK (
            holding_period_days > 0
        ),

    CONSTRAINT chk_var_confidence
        CHECK (
            confidence_level > 0
            AND confidence_level < 1
        ),

    CONSTRAINT chk_var_observations
        CHECK (
            historical_observations > 0
        ),

    CONSTRAINT chk_var_tail_observations
        CHECK (
            tail_observations IS NULL
            OR tail_observations > 0
        ),

    CONSTRAINT chk_var_pct
        CHECK (
            var_pct >= 0
        ),

    CONSTRAINT chk_var_amount
        CHECK (
            var_amount >= 0
        ),

    CONSTRAINT chk_var_expected_shortfall
        CHECK (
            expected_shortfall_pct IS NULL
            OR expected_shortfall_pct >= 0
        ),

    CONSTRAINT chk_var_expected_shortfall_amount
        CHECK (
            expected_shortfall_amount IS NULL
            OR expected_shortfall_amount >= 0
        ),


    -- -----------------------------------------------------
    -- EXPECTED SHORTFALL SHOULD NOT BE BELOW VAR
    -- WHEN EXPECTED SHORTFALL IS PRESENT
    -- -----------------------------------------------------

    CONSTRAINT chk_var_es_vs_var
        CHECK (
            expected_shortfall_pct IS NULL
            OR expected_shortfall_pct >= var_pct
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_var_result_portfolio
ON risk_platform.fact_var_result (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_var_result_method
ON risk_platform.fact_var_result (
    method
);


CREATE INDEX IF NOT EXISTS idx_var_result_confidence
ON risk_platform.fact_var_result (
    confidence_level
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_var_result IS
'Portfolio Value-at-Risk and Expected Shortfall results by methodology, confidence level and holding period.';


COMMENT ON COLUMN risk_platform.fact_var_result.var_pct IS
'Value-at-Risk expressed as a positive fraction of portfolio value; 0.02 represents 2%.';


COMMENT ON COLUMN risk_platform.fact_var_result.expected_shortfall_pct IS
'Average loss beyond the VaR threshold, expressed as a positive fraction of portfolio value.';