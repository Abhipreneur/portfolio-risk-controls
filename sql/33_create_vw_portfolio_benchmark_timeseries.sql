-- =========================================================
-- INSTITUTIONAL PORTFOLIO RISK & CONTROLS PLATFORM
-- POWER BI VIEW
-- PORTFOLIO VS BENCHMARK TIME SERIES
-- =========================================================


CREATE OR REPLACE VIEW
risk_platform.vw_portfolio_benchmark_timeseries
AS


SELECT

    -- -----------------------------------------------------
    -- IDENTIFIERS
    -- -----------------------------------------------------

    b.return_date,

    b.portfolio_id,

    dp.portfolio_name,

    b.benchmark,


    -- -----------------------------------------------------
    -- DAILY RETURNS
    -- -----------------------------------------------------

    b.portfolio_return,

    b.benchmark_return,

    b.active_return,


    -- Percentage versions for Power BI display

    b.portfolio_return
        * 100
        AS portfolio_return_pct,

    b.benchmark_return
        * 100
        AS benchmark_return_pct,

    b.active_return
        * 100
        AS active_return_pct,


    -- -----------------------------------------------------
    -- CUMULATIVE PERFORMANCE
    -- -----------------------------------------------------

    b.portfolio_growth,

    b.benchmark_growth,

    (
        b.portfolio_growth - 1
    ) * 100
        AS portfolio_cumulative_return_pct,

    (
        b.benchmark_growth - 1
    ) * 100
        AS benchmark_cumulative_return_pct,


    -- -----------------------------------------------------
    -- DRAWDOWN
    -- -----------------------------------------------------

    p.running_peak,

    p.drawdown,

    p.drawdown
        * 100
        AS drawdown_pct


FROM risk_platform.fact_benchmark_daily_return b


JOIN risk_platform.fact_portfolio_daily_return p

    ON b.return_date =
       p.return_date

    AND b.portfolio_id =
        p.portfolio_id


JOIN risk_platform.dim_portfolio dp

    ON b.portfolio_id =
       dp.portfolio_id;