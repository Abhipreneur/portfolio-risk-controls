-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT CONTROL RESULT
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_control_result (

    control_result_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    control_id VARCHAR(30) NOT NULL,

    entity_type VARCHAR(30) NOT NULL,

    entity_name VARCHAR(150) NOT NULL,

    metric_value NUMERIC(24, 12) NOT NULL,

    warning_threshold NUMERIC(18, 6) NOT NULL,

    critical_threshold NUMERIC(18, 6) NOT NULL,

    status VARCHAR(10) NOT NULL,

    exception_description TEXT,


    -- -----------------------------------------------------
    -- FOREIGN KEYS
    -- -----------------------------------------------------

    CONSTRAINT fk_control_result_portfolio
        FOREIGN KEY (portfolio_id)
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),

    CONSTRAINT fk_control_result_control
        FOREIGN KEY (control_id)
        REFERENCES risk_platform.dim_risk_limit (
            control_id
        ),


    -- -----------------------------------------------------
    -- VALID ENTITY TYPES
    -- -----------------------------------------------------

    CONSTRAINT chk_control_result_entity_type
        CHECK (
            entity_type IN (
                'Security',
                'Sector',
                'Portfolio'
            )
        ),


    -- -----------------------------------------------------
    -- VALID STATUS
    -- -----------------------------------------------------

    CONSTRAINT chk_control_result_status
        CHECK (
            status IN (
                'GREEN',
                'AMBER',
                'RED'
            )
        ),


    -- -----------------------------------------------------
    -- THRESHOLD RECONCILIATION
    -- -----------------------------------------------------

    CONSTRAINT chk_control_result_thresholds
        CHECK (
            critical_threshold
            >= warning_threshold
        ),


    -- -----------------------------------------------------
    -- STATUS RECONCILIATION
    --
    -- Current control framework assumes:
    -- higher metric values = higher risk.
    -- -----------------------------------------------------

    CONSTRAINT chk_control_result_status_reconciliation
        CHECK (
            (
                metric_value >= critical_threshold
                AND status = 'RED'
            )
            OR
            (
                metric_value >= warning_threshold
                AND metric_value < critical_threshold
                AND status = 'AMBER'
            )
            OR
            (
                metric_value < warning_threshold
                AND status = 'GREEN'
            )
        ),


    -- -----------------------------------------------------
    -- PREVENT DUPLICATE DAILY CONTROL RESULTS
    -- -----------------------------------------------------

    CONSTRAINT uq_control_result
        UNIQUE (
            valuation_date,
            portfolio_id,
            control_id,
            entity_type,
            entity_name
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_control_result_date
ON risk_platform.fact_control_result (
    valuation_date
);


CREATE INDEX IF NOT EXISTS idx_control_result_portfolio
ON risk_platform.fact_control_result (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_control_result_control
ON risk_platform.fact_control_result (
    control_id
);


CREATE INDEX IF NOT EXISTS idx_control_result_status
ON risk_platform.fact_control_result (
    status
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_control_result IS
'Daily automated portfolio risk-control evaluation results.';


COMMENT ON COLUMN risk_platform.fact_control_result.warning_threshold IS
'Snapshot of the warning threshold used when the control was evaluated.';


COMMENT ON COLUMN risk_platform.fact_control_result.critical_threshold IS
'Snapshot of the critical threshold used when the control was evaluated.';