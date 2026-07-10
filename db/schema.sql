-- ==========================================
-- Nifty100 Financial Intelligence Database
-- Sprint 1 - Day 4
-- SQLite Schema
-- ==========================================

PRAGMA foreign_keys = ON;

-- ==========================================
-- 1. Companies
-- ==========================================

CREATE TABLE IF NOT EXISTS companies (

    id TEXT PRIMARY KEY,
    company_logo TEXT,
    company_name TEXT NOT NULL,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL

);

-- ==========================================
-- 2. Profit & Loss
-- ==========================================

CREATE TABLE IF NOT EXISTS profit_loss (

    id TEXT,
    year INTEGER,

    sales REAL,
    expenses REAL,
    operating_profit REAL,
    operating_profit_margin REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax REAL,
    net_profit REAL,
    eps REAL,

    PRIMARY KEY(id, year),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 3. Balance Sheet
-- ==========================================

CREATE TABLE IF NOT EXISTS balance_sheet (

    id TEXT,
    year INTEGER,

    equity_share_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,

    fixed_assets REAL,
    investments REAL,
    other_assets REAL,
    total_assets REAL,

    PRIMARY KEY(id, year),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 4. Cash Flow
-- ==========================================

CREATE TABLE IF NOT EXISTS cash_flow (

    id TEXT,
    year INTEGER,

    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    PRIMARY KEY(id, year),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 5. Quarterly Results
-- ==========================================

CREATE TABLE IF NOT EXISTS quarterly_results (

    id TEXT,
    quarter TEXT,

    sales REAL,
    expenses REAL,
    operating_profit REAL,
    net_profit REAL,
    eps REAL,

    PRIMARY KEY(id, quarter),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 6. Shareholding Pattern
-- ==========================================

CREATE TABLE IF NOT EXISTS shareholding_pattern (

    id TEXT,
    year INTEGER,

    promoters REAL,
    fii REAL,
    dii REAL,
    public REAL,

    PRIMARY KEY(id, year),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 7. Stock Prices
-- ==========================================

CREATE TABLE IF NOT EXISTS stock_prices (

    id TEXT,
    trade_date DATE,

    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,

    PRIMARY KEY(id, trade_date),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 8. Dividends
-- ==========================================

CREATE TABLE IF NOT EXISTS dividends (

    id TEXT,
    year INTEGER,

    dividend REAL,

    PRIMARY KEY(id, year),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 9. Corporate Actions
-- ==========================================

CREATE TABLE IF NOT EXISTS corporate_actions (

    action_id INTEGER PRIMARY KEY AUTOINCREMENT,

    id TEXT,

    action_date DATE,

    action_type TEXT,

    remarks TEXT,

    FOREIGN KEY(id)
    REFERENCES companies(id)

);

-- ==========================================
-- 10. Ratios
-- ==========================================

CREATE TABLE IF NOT EXISTS ratios (

    id TEXT,
    year INTEGER,

    pe_ratio REAL,
    pb_ratio REAL,
    roe REAL,
    roce REAL,
    debt_to_equity REAL,
    current_ratio REAL,

    PRIMARY KEY(id, year),

    FOREIGN KEY(id)
    REFERENCES companies(id)

);