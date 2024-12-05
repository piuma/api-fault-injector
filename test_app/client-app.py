#!/usr/bin/env python3
import sys
import time
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import yaml


def timeit(do_print=False):
    def tmp(method):
        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            elapsed = time.time() - ts
            # print("Function: %r took: %2.4f sec" % (method.__name__, elapsed), end="", flush=True)
            print(".", end="", flush=True)
            if isinstance(result, dict):
                result.update({"elapsed": elapsed})
            return result

        return timed

    return tmp


@timeit()
def _request(url="http://localhost:5000/api/data", use_proxy=True):
    try:
        proxies = {}
        if use_proxy:
            proxies = {
                "http": "http://localhost:8899",
                "https": "http://localhost:8899",
            }

        response = requests.get(url, proxies=proxies, timeout=2)
        if response.status_code == 200:
            return {"error": 0, "status_code": response.status_code}
        else:
            return {"error": 1, "status_code": response.status_code}
    except Exception as e:
        print(f"Request failed: {e}")
        return {"error": 1, "status_code": -1}


def main(request_count, batch_count, host, debug, error):
    results = []

    test_f = lambda: _request(use_proxy=True)  # noqa: E731

    ts = time.time()
    with ThreadPoolExecutor(max_workers=batch_count) as executor:
        futures = [executor.submit(test_f) for _ in range(request_count)]
        for future in as_completed(futures):
            results.append(future.result())

    error_series = [r for r in results if r["error"]]
    success_series = [r for r in results if not r["error"]]

    stats = {
        "error": get_stats(error_series),
        "success": get_stats(success_series),
        "count": request_count,
        "batch": batch_count,
        "elapsed": round(time.time() - ts, 3),
    }

    print()
    yaml.dump(stats, sys.stdout)


def get_stats(data):
    ret = {
        "min": round(min([r["elapsed"] for r in data], default=0), 2),
        "max": round(max([r["elapsed"] for r in data], default=0), 2),
        "count": len(data),
        "avg": (
            round(sum([r["elapsed"] for r in data]) / len(data), 2) if len(data) else 0
        ),
    }
    ret["variance"] = (
        round(sum([(r["elapsed"] - ret["avg"]) ** 2 for r in data]) / ret["count"], 2)
        if ret["count"]
        else 0
    )
    return ret


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--count", type=int, default=10)
    parser.add_argument("-b", "--batch", type=int, default=1)
    parser.add_argument("-d", "--debug", type=int, default=5)
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--error", type=int, default=0)

    args = parser.parse_args()
    main(
        request_count=args.count,
        batch_count=args.batch,
        host=args.host,
        debug=args.debug,
        error=args.error,
    )
