PRAGMA foreign_keys = ON;

-- ==========================================
-- 1. Companies
-- ==========================================
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    company_logo TEXT,
    company_name TEXT,
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
    net_profit REAL,
    eps REAL,
    PRIMARY KEY(id, year),
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 3. Balance Sheet
-- ==========================================
CREATE TABLE IF NOT EXISTS balance_sheet (
    id TEXT,
    year INTEGER,
    total_assets REAL,
    total_liabilities REAL,
    equity REAL,
    reserves REAL,
    borrowings REAL,
    PRIMARY KEY(id, year),
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 4. Cash Flow
-- ==========================================
CREATE TABLE IF NOT EXISTS cash_flow (
    id TEXT,
    year INTEGER,
    operating_cash REAL,
    investing_cash REAL,
    financing_cash REAL,
    net_cash_flow REAL,
    PRIMARY KEY(id, year),
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 5. Financial Ratios
-- ==========================================
CREATE TABLE IF NOT EXISTS ratios (
    id TEXT,
    year INTEGER,
    pe_ratio REAL,
    pb_ratio REAL,
    roe REAL,
    roce REAL,
    debt_equity REAL,
    current_ratio REAL,
    PRIMARY KEY(id, year),
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 6. Analysis
-- ==========================================
CREATE TABLE IF NOT EXISTS analysis (
    id TEXT PRIMARY KEY,
    analysis TEXT,
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 7. Market Cap
-- ==========================================
CREATE TABLE IF NOT EXISTS market_cap (
    id TEXT PRIMARY KEY,
    market_cap REAL,
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 8. Peer Groups
-- ==========================================
CREATE TABLE IF NOT EXISTS peer_groups (
    id TEXT,
    peer_company TEXT,
    PRIMARY KEY(id, peer_company),
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 9. Pros and Cons
-- ==========================================
CREATE TABLE IF NOT EXISTS pros_and_cons (
    id TEXT,
    type TEXT,
    description TEXT,
    PRIMARY KEY(id, type, description),
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 10. Sectors
-- ==========================================
CREATE TABLE IF NOT EXISTS sectors (
    id TEXT PRIMARY KEY,
    sector TEXT,
    industry TEXT,
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 11. Documents
-- ==========================================
CREATE TABLE IF NOT EXISTS documents (
    id TEXT,
    document_name TEXT,
    document_url TEXT,
    PRIMARY KEY(id, document_name),
    FOREIGN KEY(id) REFERENCES companies(id)
);

-- ==========================================
-- 12. Stock Prices
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
    FOREIGN KEY(id) REFERENCES companies(id)
);