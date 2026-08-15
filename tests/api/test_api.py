import urllib.request
import json


BASE_URL = "http://127.0.0.1:8000"


def check_endpoint(path):
    """Check an API endpoint and print its response."""
    url = BASE_URL + path

    print("\n" + "=" * 60)
    print("Testing:", url)

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status = response.status
            data = response.read().decode("utf-8")

            print("Status:", status)

            if status == 200:
                print("PASS")
                print("Response:")
                print(json.dumps(json.loads(data), indent=2)[:1000])
                return True
            else:
                print("FAIL")
                return False

    except Exception as e:
        print("ERROR:", e)
        return False


def test_api_endpoints():
    """Test all major Nifty100 API endpoints."""

    endpoints = [
        "/api/v1/health",
        "/api/v1",
        "/api/v1/companies",
        "/api/v1/companies/SBIN",
        "/api/v1/companies/ATGL",
        "/api/v1/companies/search/query?q=tata",

        "/api/v1/financials/SBIN",
        "/api/v1/financials/SBIN/latest",
        "/api/v1/financials/SBIN/cagr",
        "/api/v1/financials/SBIN/valuation",

        "/api/v1/financials/ATGL",
        "/api/v1/financials/ATGL/latest",
        "/api/v1/financials/ATGL/cagr",
        "/api/v1/financials/ATGL/valuation",

        "/api/v1/screener?limit=10",
        "/api/v1/screener?min_roe=20&limit=20",
        "/api/v1/screener?max_debt_equity=1&limit=20",
    ]

    print("\n" + "=" * 60)
    print("NIFTY100 FINANCIAL INTELLIGENCE API TEST")
    print("=" * 60)

    failures = []

    for endpoint in endpoints:
        if not check_endpoint(endpoint):
            failures.append(endpoint)

    print("\n" + "=" * 60)
    print("API TEST COMPLETED")
    print("=" * 60)

    if failures:
        print("\nFAILED ENDPOINTS:")
        for endpoint in failures:
            print(" -", endpoint)

        raise AssertionError(
            f"{len(failures)} API endpoint(s) failed"
        )

    print("\nAll API endpoints passed.")


if __name__ == "__main__":
    test_api_endpoints()
