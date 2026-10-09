-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- FACT BENCHMARK DAILY RETURN
-- =========================================================


CREATE TABLE IF NOT EXISTS risk_platform.fact_benchmark_daily_return (

    return_date DATE NOT NULL,

    portfolio_id VARCHAR(30) NOT NULL,

    benchmark VARCHAR(100) NOT NULL,

    portfolio_return NUMERIC(24, 15) NOT NULL,

    benchmark_return NUMERIC(24, 15) NOT NULL,

    active_return NUMERIC(24, 15) NOT NULL,

    portfolio_growth NUMERIC(24, 15) NOT NULL,

    benchmark_growth NUMERIC(24, 15) NOT NULL,


    -- -----------------------------------------------------
    -- PRIMARY KEY
    -- -----------------------------------------------------

    CONSTRAINT pk_benchmark_daily_return
        PRIMARY KEY (
            return_date,
            portfolio_id,
            benchmark
        ),


    -- -----------------------------------------------------
    -- FOREIGN KEY
    -- -----------------------------------------------------

    CONSTRAINT fk_benchmark_daily_return_portfolio
        FOREIGN KEY (
            portfolio_id
        )
        REFERENCES risk_platform.dim_portfolio (
            portfolio_id
        ),


    -- -----------------------------------------------------
    -- DATA QUALITY CHECKS
    -- -----------------------------------------------------

    CONSTRAINT chk_benchmark_daily_portfolio_growth
        CHECK (
            portfolio_growth > 0
        ),

    CONSTRAINT chk_benchmark_daily_benchmark_growth
        CHECK (
            benchmark_growth > 0
        ),


    -- active return = portfolio return - benchmark return

    CONSTRAINT chk_benchmark_daily_active_return
        CHECK (
            ABS(
                active_return
                -
                (
                    portfolio_return
                    - benchmark_return
                )
            ) <= 0.000000000001
        )
);


-- ---------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_benchmark_daily_portfolio
ON risk_platform.fact_benchmark_daily_return (
    portfolio_id
);


CREATE INDEX IF NOT EXISTS idx_benchmark_daily_date
ON risk_platform.fact_benchmark_daily_return (
    return_date
);


CREATE INDEX IF NOT EXISTS idx_benchmark_daily_benchmark
ON risk_platform.fact_benchmark_daily_return (
    benchmark
);


-- ---------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------

COMMENT ON TABLE risk_platform.fact_benchmark_daily_return IS
'Daily aligned portfolio and benchmark returns used for benchmark-relative risk analytics.';


COMMENT ON COLUMN risk_platform.fact_benchmark_daily_return.active_return IS
'Portfolio daily return minus benchmark daily return.';


COMMENT ON COLUMN risk_platform.fact_benchmark_daily_return.portfolio_growth IS
'Cumulative growth index of the simulated portfolio return series.';


COMMENT ON COLUMN risk_platform.fact_benchmark_daily_return.benchmark_growth IS
'Cumulative growth index of the benchmark return series.';