# ============================================================
# NIFTY100 FINANCIAL INTELLIGENCE
# Project Makefile
# ============================================================

PYTHON := python3
PYTEST := $(PYTHON) -m pytest

# ------------------------------------------------------------
# DAY 05 — Load all Excel files
# ------------------------------------------------------------
load:
	$(PYTHON) src/etl/loader.py

# ------------------------------------------------------------
# SPRINT 2 — Generate financial ratios
# ------------------------------------------------------------
ratios:
	$(PYTHON) src/analytics/ratios.py

# ------------------------------------------------------------
# TEST — Run complete pytest suite
# ------------------------------------------------------------
test:
	PYTHONPATH=. $(PYTEST) -v

# ------------------------------------------------------------
# REPORT — Generate company, sector and portfolio reports
# ------------------------------------------------------------
report:
	$(PYTHON) src/reports/run_day34_batch.py

# ------------------------------------------------------------
# DASHBOARD — Launch Streamlit
# ------------------------------------------------------------
dashboard:
	streamlit run src/dashboard/app.py

# ------------------------------------------------------------
# API — Launch FastAPI
# ------------------------------------------------------------
api:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# ------------------------------------------------------------
# CLEAN — Remove Python cache and test artifacts
# Database is NOT deleted
# ------------------------------------------------------------
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache

.PHONY: load ratios test report dashboard api clean
