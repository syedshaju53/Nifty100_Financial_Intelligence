
import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.health import router as health_router
from src.api.routers.financials import router as financials_router
from src.api.routers.companies import router as companies_router
from src.api.routers.screener import router as screener_router
from src.api.routers.sectors import router as sectors_router
from src.api.routers.peers import router as peers_router
from src.api.routers.valuation import router as valuation_router
from src.api.routers.portfolio import router as portfolio_router
from src.api.routers.documents import router as documents_router


START_TIME = time.time()


app = FastAPI(
    title="Nifty100 Financial Intelligence API",
    description=(
        "Backend API for financial analytics, company screening, "
        "investment intelligence, clustering and financial KPIs."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    start = time.time()

    response = await call_next(request)

    elapsed = time.time() - start

    print(
        f"[API] {request.method} "
        f"{request.url.path} "
        f"-> {response.status_code} "
        f"({elapsed:.4f}s)"
    )

    return response


# --------------------------------------------------
# REGISTER ROUTERS
# --------------------------------------------------

ROUTERS = [
    health_router,
    financials_router,
    companies_router,
    screener_router,
    sectors_router,
    peers_router,
    valuation_router,
    portfolio_router,
    documents_router,
]

for api_router in ROUTERS:
    app.include_router(api_router)


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Nifty100 Financial Intelligence API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
        "companies": "/api/v1/companies",
    }


# --------------------------------------------------
# API INFO
# --------------------------------------------------

@app.get("/api/v1")
def api_info():
    return {
        "name": "Nifty100 Financial Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "uptime_seconds": round(
            time.time() - START_TIME,
            2,
        ),
        "endpoints": {
            "health": "/api/v1/health",
            "companies": "/api/v1/companies",
            "company": "/api/v1/companies/{company_id}",
            "search": "/api/v1/companies/search/query?q=...",
            "financials": "/api/v1/financials/{company_id}",
            "latest_financials": "/api/v1/financials/{company_id}/latest",
            "cagr": "/api/v1/financials/{company_id}/cagr",
            "financial_valuation": "/api/v1/financials/{company_id}/valuation",
            "screener": "/api/v1/screener",
            "sectors": "/api/v1/sectors",
            "sector_companies": "/api/v1/sectors/{sector}/companies",
            "peers": "/api/v1/peers",
            "peer_group": "/api/v1/peers/{peer_group_name}",
            "market_cap": "/api/v1/market-cap/{company_id}",
            "portfolio": "/api/v1/portfolio",
            "documents": "/api/v1/companies/{company_id}/documents",
        },
    }

