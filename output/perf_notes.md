# Day 43 — Performance & Integration Testing

## 1. API Load Test

Endpoint:

GET /api/v1/screener?min_roe=15

Test configuration:
- Concurrent requests: 10
- Python ThreadPoolExecutor workers: 10
- Request timeout: 10 seconds

Result:
- Total execution time: 0.055 seconds
- Successful requests: 10/10
- HTTP 200 responses: 10/10
- Test result: PASS

Individual request times:
- Request 1: 0.050 sec
- Request 2: 0.043 sec
- Request 3: 0.050 sec
- Request 4: 0.052 sec
- Request 5: 0.048 sec
- Request 6: 0.038 sec
- Request 7: 0.053 sec
- Request 8: 0.042 sec
- Request 9: 0.046 sec
- Request 10: 0.052 sec

Performance requirement:
All 10 requests must complete within 10 seconds.

Result: PASS.

## 2. Company Profile API Performance

Five companies were tested:

| Company | HTTP Status | Response Time |
|---|---:|---:|
| TCS | 200 | 0.016959 sec |
| INFY | 200 | 0.002880 sec |
| RELIANCE | 200 | 0.002659 sec |
| TATAMOTORS | 200 | 0.002812 sec |
| HDFCBANK | 200 | 0.005718 sec |

All API responses were below the 3-second target.

Result: PASS.

## 3. SQLite Query Optimisation

Indexes created:

- idx_profit_loss_company_year
- idx_balance_sheet_company_year
- idx_cash_flow_company_year
- idx_financial_ratios_company_year
- idx_stock_prices_company_date
- idx_documents_company_year

All indexes were verified using SQLite PRAGMA index_list and PRAGMA index_info.

Result: PASS.

## 4. FastAPI Availability

FastAPI health endpoint:

GET /api/v1/health

Result:
- HTTP status: 200
- API status: ok
- Database status: connected
- Companies: 92

Result: PASS.

## 5. Streamlit Availability

Streamlit was verified on port 8501.

HTTP response:
- Status: 200
- Server: TornadoServer

Result: PASS.

## 6. Application Ports

FastAPI:
- Port 8000

Streamlit:
- Port 8501

Both services responded successfully without a port conflict.

Result: PASS.

## 7. Performance Bottlenecks

No significant API performance bottlenecks were identified during Day 43 testing.

SQLite indexes were added to frequently queried historical tables to improve company/year-based lookups.

## 8. Final Integration Verification

The Streamlit dashboard and FastAPI services must be verified together, including confirmation that dashboard screener results match the API screener results.

