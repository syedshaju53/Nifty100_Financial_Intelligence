-- =====================================================
-- Nifty100 Financial Intelligence
-- Exploratory SQL Queries
-- =====================================================

-- Query 1: Total number of companies
SELECT COUNT(*) AS total_companies
FROM companies;

--------------------------------------------------------

-- Query 2: List all companies
SELECT id, company_name
FROM companies
ORDER BY company_name;

--------------------------------------------------------

-- Query 3: Top 10 companies by ROE
SELECT id,
       company_name,
       roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10;

--------------------------------------------------------

-- Query 4: Top 10 companies by ROCE
SELECT id,
       company_name,
       roce_percentage
FROM companies
ORDER BY roce_percentage DESC
LIMIT 10;

--------------------------------------------------------

-- Query 5: Average Book Value
SELECT ROUND(AVG(book_value),2) AS average_book_value
FROM companies;

--------------------------------------------------------

-- Query 6: Companies with Face Value greater than 10
SELECT id,
       company_name,
       face_value
FROM companies
WHERE face_value > 10
ORDER BY face_value DESC;

--------------------------------------------------------

-- Query 7: Number of stock price records
SELECT COUNT(*) AS total_stock_records
FROM stock_prices;

--------------------------------------------------------

-- Query 8: Number of balance sheet records
SELECT COUNT(*) AS balance_sheet_records
FROM balance_sheet;

--------------------------------------------------------

-- Query 9: Number of profit & loss records
SELECT COUNT(*) AS profit_loss_records
FROM profit_loss;

--------------------------------------------------------

-- Query 10: Record count of every table
SELECT 'companies' AS table_name, COUNT(*) AS total_rows FROM companies
UNION ALL
SELECT 'profit_loss', COUNT(*) FROM profit_loss
UNION ALL
SELECT 'balance_sheet', COUNT(*) FROM balance_sheet
UNION ALL
SELECT 'cash_flow', COUNT(*) FROM cash_flow
UNION ALL
SELECT 'analysis', COUNT(*) FROM analysis
UNION ALL
SELECT 'pros_and_cons', COUNT(*) FROM pros_and_cons
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'stock_prices', COUNT(*) FROM stock_prices
UNION ALL
SELECT 'ratios', COUNT(*) FROM ratios
UNION ALL
SELECT 'market_cap', COUNT(*) FROM market_cap
UNION ALL
SELECT 'peer_groups', COUNT(*) FROM peer_groups
UNION ALL
SELECT 'sectors', COUNT(*) FROM sectors;