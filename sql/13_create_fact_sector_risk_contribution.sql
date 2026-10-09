-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT SECTOR RISK CONTRIBUTION
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_sector_risk_contribution (

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    sector VARCHAR(100) NOT NULL,

    security_count INTEGER NOT NULL,

    portfolio_weight_pct NUMERIC(24, 12) NOT NULL,

    risk_contribution_pct NUMERIC(24, 12) NOT NULL,

    risk_minus_weight_pct NUMERIC(24, 12) NOT NULL,

    risk_to_weight_ratio NUMERIC(24, 15) NOT NULL,

    component_annualized_volatility NUMERIC(24, 15) NOT NULL,

    risk_contribution_rank INTEGER NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_sector_risk_contribution
        PRIMARY KEY (
            valuation_date,
            portfolio_id,
            sector
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEY TO PORTFOLIO
    -- -----------------------------------------------------

    CONSTRAINT fk_sector_risk_contribution_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_sector_risk_security_count
        CHECK (
            security_count > 0
        ),

    CONSTRAINT chk_sector_risk_weight
        CHECK (
            portfolio_weight_pct > 0
            AND portfolio_weight_pct <= 100
        ),

    CONSTRAINT chk_sector_risk_rank
        CHECK (
            risk_contribution_rank > 0
        ),


    -- -----------------------------------------------------
    -- RISK MINUS WEIGHT RECONCILIATION
    -- -----------------------------------------------------

    CONSTRAINT chk_sector_risk_minus_weight
        CHECK (
            ABS(
                risk_minus_weight_pct
                -
                (
                    risk_contribution_pct
                    - portfolio_weight_pct
                )
            ) <= 0.000001
        ),


    -- -----------------------------------------------------
    -- RISK / WEIGHT RATIO RECONCILIATION
    -- -----------------------------------------------------

    CONSTRAINT chk_sector_risk_weight_ratio
        CHECK (
            ABS(
                risk_to_weight_ratio
                -
                (
                    risk_contribution_pct
                    / portfolio_weight_pct
                )
            ) <= 0.000001
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_sector_risk_portfolio
ON risk_platform.fact_sector_risk_contribution (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_sector_risk_sector
ON risk_platform.fact_sector_risk_contribution (
    sector
);


CREATE INDEX IF NOT EXISTS idx_sector_risk_rank
ON risk_platform.fact_sector_risk_contribution (
    risk_contribution_rank
);


CREATE INDEX IF NOT EXISTS idx_sector_risk_contribution
ON risk_platform.fact_sector_risk_contribution (
    risk_contribution_pct
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_sector_risk_contribution IS
'Sector-level aggregation of portfolio volatility risk contribution.';


COMMENT ON COLUMN risk_platform.fact_sector_risk_contribution.risk_minus_weight_pct IS
'Risk contribution percentage minus portfolio allocation percentage.';


COMMENT ON COLUMN risk_platform.fact_sector_risk_contribution.risk_to_weight_ratio IS
'Sector risk contribution percentage divided by sector portfolio weight percentage.';