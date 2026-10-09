-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT POSITION TABLE
-- =========================================================


-- ---------------------------------------------------------
-- FACT: PORTFOLIO POSITION
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS risk_platform.fact_position (

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    security_id INTEGER NOT NULL,

    target_weight_pct NUMERIC(18, 10) NOT NULL,

    actual_weight_pct NUMERIC(18, 10) NOT NULL,

    weight_difference_pct NUMERIC(18, 10) NOT NULL,

    target_value NUMERIC(20, 2) NOT NULL,

    quantity BIGINT NOT NULL,

    market_price NUMERIC(20, 10) NOT NULL,

    market_value NUMERIC(20, 2) NOT NULL,

    allocation_difference NUMERIC(20, 2) NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    --
    -- One security can appear only once per portfolio
    -- for a given valuation date.
    -- -----------------------------------------------------

    CONSTRAINT pk_fact_position
        PRIMARY KEY (
            valuation_date,
            portfolio_id,
            security_id
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEYS
    -- -----------------------------------------------------

    CONSTRAINT fk_fact_position_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),


    CONSTRAINT fk_fact_position_security
        FOREIGN KEY (
            security_id
        )
        REFERENCES risk_platform.dim_security (
            security_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_position_target_weight
        CHECK (
            target_weight_pct >= 0
            AND target_weight_pct <= 100
        ),


    CONSTRAINT chk_position_actual_weight
        CHECK (
            actual_weight_pct >= 0
            AND actual_weight_pct <= 100
        ),


    CONSTRAINT chk_position_target_value
        CHECK (
            target_value >= 0
        ),


    CONSTRAINT chk_position_quantity
        CHECK (
            quantity >= 0
        ),


    CONSTRAINT chk_position_market_price
        CHECK (
            market_price > 0
        ),


    CONSTRAINT chk_position_market_value
        CHECK (
            market_value >= 0
        ),


    -- -----------------------------------------------------
    -- MARKET VALUE RECONCILIATION
    --
    -- market_value should equal:
    -- quantity × market_price
    --
    -- Allow ₹0.01 tolerance for numeric rounding.
    -- -----------------------------------------------------

    CONSTRAINT chk_position_market_value_reconciliation
        CHECK (
            ABS(
                market_value
                - (
                    quantity
                    * market_price
                )
            ) <= 0.01
        ),


    -- -----------------------------------------------------
    -- WEIGHT DIFFERENCE RECONCILIATION
    --
    -- weight_difference_pct should equal:
    -- actual_weight_pct - target_weight_pct
    -- -----------------------------------------------------

    CONSTRAINT chk_position_weight_difference
        CHECK (
            ABS(
                weight_difference_pct
                - (
                    actual_weight_pct
                    - target_weight_pct
                )
            ) <= 0.000001
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_fact_position_portfolio
ON risk_platform.fact_position (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_fact_position_security
ON risk_platform.fact_position (
    security_id
);


CREATE INDEX IF NOT EXISTS idx_fact_position_valuation_date
ON risk_platform.fact_position (
    valuation_date
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_position IS
'Portfolio security positions by valuation date. Stores weights, quantities, prices and market values.';


COMMENT ON COLUMN risk_platform.fact_position.weight_difference_pct IS
'Actual portfolio weight minus target portfolio weight.';


COMMENT ON COLUMN risk_platform.fact_position.allocation_difference IS
'Target position value minus actual market value after whole-share allocation.';