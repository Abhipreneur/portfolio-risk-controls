-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT LIQUIDITY
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_liquidity (

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    security_id INTEGER NOT NULL,

    adv_lookback_days INTEGER NOT NULL,

    adv_shares NUMERIC(24, 6) NOT NULL,

    position_pct_adv NUMERIC(24, 12) NOT NULL,

    max_participation_rate NUMERIC(18, 10) NOT NULL,

    daily_liquidation_capacity NUMERIC(24, 6) NOT NULL,

    days_to_liquidate NUMERIC(24, 12) NOT NULL,

    liquidity_class VARCHAR(20) NOT NULL,

    liquidity_rank INTEGER NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_fact_liquidity
        PRIMARY KEY (
            valuation_date,
            portfolio_id,
            security_id
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEY TO POSITION
    --
    -- Ensures every liquidity record corresponds
    -- to an actual portfolio position.
    -- -----------------------------------------------------

    CONSTRAINT fk_liquidity_position
        FOREIGN KEY (
            valuation_date,
            portfolio_id,
            security_id
        )
        REFERENCES risk_platform.fact_position (
            valuation_date,
            portfolio_id,
            security_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_liquidity_lookback
        CHECK (
            adv_lookback_days > 0
        ),

    CONSTRAINT chk_liquidity_adv
        CHECK (
            adv_shares > 0
        ),

    CONSTRAINT chk_liquidity_position_pct_adv
        CHECK (
            position_pct_adv >= 0
        ),

    CONSTRAINT chk_liquidity_participation_rate
        CHECK (
            max_participation_rate > 0
            AND max_participation_rate <= 1
        ),

    CONSTRAINT chk_liquidity_capacity
        CHECK (
            daily_liquidation_capacity > 0
        ),

    CONSTRAINT chk_liquidity_days
        CHECK (
            days_to_liquidate >= 0
        ),

    CONSTRAINT chk_liquidity_class
        CHECK (
            liquidity_class IN (
                'HIGH',
                'MEDIUM',
                'LOW'
            )
        ),

    CONSTRAINT chk_liquidity_rank
        CHECK (
            liquidity_rank > 0
        ),


    -- -----------------------------------------------------
    -- CAPACITY RECONCILIATION
    --
    -- daily liquidation capacity should equal:
    -- ADV × participation rate
    -- -----------------------------------------------------

    CONSTRAINT chk_liquidity_capacity_reconciliation
        CHECK (
            ABS(
                daily_liquidation_capacity
                -
                (
                    adv_shares
                    * max_participation_rate
                )
            ) <= 0.01
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_liquidity_portfolio
ON risk_platform.fact_liquidity (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_liquidity_security
ON risk_platform.fact_liquidity (
    security_id
);


CREATE INDEX IF NOT EXISTS idx_liquidity_class
ON risk_platform.fact_liquidity (
    liquidity_class
);


CREATE INDEX IF NOT EXISTS idx_liquidity_days
ON risk_platform.fact_liquidity (
    days_to_liquidate
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_liquidity IS
'Security-level portfolio liquidity analytics including ADV and estimated days to liquidate.';

COMMENT ON COLUMN risk_platform.fact_liquidity.max_participation_rate IS
'Maximum fraction of average daily trading volume assumed available for liquidation.';

COMMENT ON COLUMN risk_platform.fact_liquidity.days_to_liquidate IS
'Estimated trading days required to liquidate the position at the configured participation rate.';