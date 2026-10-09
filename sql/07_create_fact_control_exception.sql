-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT CONTROL EXCEPTION
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_control_exception (

    exception_id VARCHAR(30) PRIMARY KEY,

    control_result_id BIGINT NOT NULL,

    exception_status VARCHAR(30) NOT NULL,

    exception_description TEXT,


    -- -----------------------------------------------------
    -- FOREIGN KEY TO ORIGINAL CONTROL RESULT
    -- -----------------------------------------------------

    CONSTRAINT fk_control_exception_result
        FOREIGN KEY (control_result_id)
        REFERENCES risk_platform.fact_control_result (
            control_result_id
        ),


    -- -----------------------------------------------------
    -- ONE EXCEPTION PER CONTROL RESULT
    -- -----------------------------------------------------

    CONSTRAINT uq_control_exception_result
        UNIQUE (
            control_result_id
        ),


    -- -----------------------------------------------------
    -- EXCEPTION WORKFLOW STATUS
    -- -----------------------------------------------------

    CONSTRAINT chk_control_exception_status
        CHECK (
            exception_status IN (
                'OPEN',
                'UNDER_REVIEW',
                'CLOSED',
                'WAIVED'
            )
        )
);


-- ---------------------------------------------------------
-- INDEX
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_control_exception_status
ON risk_platform.fact_control_exception (
    exception_status
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_control_exception IS
'Operational workflow table containing portfolio risk-control exceptions.';


COMMENT ON COLUMN risk_platform.fact_control_exception.control_result_id IS
'Links each exception to the exact automated control evaluation that generated it.';


COMMENT ON COLUMN risk_platform.fact_control_exception.exception_status IS
'Operational workflow status such as OPEN, UNDER_REVIEW, CLOSED or WAIVED.';