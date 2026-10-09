-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT BENCHMARK RISK SUMMARY
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_benchmark_risk_summary (

    valuation_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    benchmark VARCHAR(100) NOT NULL,

    aligned_return_observations INTEGER NOT NULL,

    start_date DATE NOT NULL,

    end_date DATE NOT NULL,

    beta NUMERIC(24, 15) NOT NULL,

    correlation NUMERIC(24, 15) NOT NULL,

    r_squared NUMERIC(24, 15) NOT NULL,

    portfolio_annualized_volatility NUMERIC(24, 15) NOT NULL,

    benchmark_annualized_volatility NUMERIC(24, 15) NOT NULL,

    annualized_tracking_error NUMERIC(24, 15) NOT NULL,

    annualized_active_return NUMERIC(24, 15) NOT NULL,

    information_ratio NUMERIC(24, 15),

    portfolio_cumulative_return NUMERIC(24, 15) NOT NULL,

    benchmark_cumulative_return NUMERIC(24, 15) NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_benchmark_risk_summary
        PRIMARY KEY (
            valuation_date,
            portfolio_id,
            benchmark
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEY
    -- -----------------------------------------------------

    CONSTRAINT fk_benchmark_risk_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_benchmark_observations
        CHECK (
            aligned_return_observations > 0
        ),

    CONSTRAINT chk_benchmark_date_range
        CHECK (
            start_date <= end_date
            AND end_date <= valuation_date
        ),

    CONSTRAINT chk_benchmark_correlation
        CHECK (
            correlation >= -1
            AND correlation <= 1
        ),

    CONSTRAINT chk_benchmark_r_squared
        CHECK (
            r_squared >= 0
            AND r_squared <= 1
        ),

    CONSTRAINT chk_benchmark_volatility
        CHECK (
            portfolio_annualized_volatility >= 0
            AND benchmark_annualized_volatility >= 0
        ),

    CONSTRAINT chk_benchmark_tracking_error
        CHECK (
            annualized_tracking_error >= 0
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_benchmark_risk_portfolio
ON risk_platform.fact_benchmark_risk_summary (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_benchmark_risk_benchmark
ON risk_platform.fact_benchmark_risk_summary (
    benchmark
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_benchmark_risk_summary IS
'Portfolio benchmark-relative analytics including beta, correlation, tracking error and information ratio.';


COMMENT ON COLUMN risk_platform.fact_benchmark_risk_summary.beta IS
'Portfolio sensitivity to benchmark returns over aligned historical observations.';


COMMENT ON COLUMN risk_platform.fact_benchmark_risk_summary.portfolio_cumulative_return IS
'Historical simulated cumulative portfolio return using current portfolio weights.';