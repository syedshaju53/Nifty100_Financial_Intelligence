import concurrent.futures
import time

import requests


API_URL = "http://127.0.0.1:8000/api/v1/screener?min_roe=15"


def make_request():
    start = time.perf_counter()

    response = requests.get(API_URL, timeout=10)

    elapsed = time.perf_counter() - start

    return {
        "status_code": response.status_code,
        "elapsed": elapsed,
    }


def test_10_concurrent_screener_requests():
    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: make_request(), range(10)))

    total_time = time.perf_counter() - start

    assert len(results) == 10

    for result in results:
        assert result["status_code"] == 200

    assert total_time < 10, (
        f"10 concurrent requests took {total_time:.2f}s"
    )

    print("\nPerformance results:")
    print(f"Total time: {total_time:.3f}s")

    for index, result in enumerate(results, start=1):
        print(
            f"Request {index}: "
            f"{result['status_code']} "
            f"{result['elapsed']:.3f}s"
        )