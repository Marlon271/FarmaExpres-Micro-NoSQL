#!/usr/bin/env python3
"""Run the demo pipeline against the local prediction API."""

import argparse
import json
import urllib.error
import urllib.request


def call(api_base, method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{api_base.rstrip('/')}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Run seed, clean, train and read predictions.")
    parser.add_argument("--api", default="http://localhost:8000", help="Prediction API base URL.")
    parser.add_argument("--products", type=int, default=15, help="Number of demo products.")
    parser.add_argument("--days", type=int, default=120, help="Number of movement history days.")
    args = parser.parse_args()

    steps = [
        ("Health", "GET", "/health", None),
        ("Seed", "POST", "/seed-test-data", {"source": "generated", "product_count": args.products, "days": args.days}),
        ("Clean", "POST", "/clean", None),
        ("Train", "POST", "/train", {"horizon_days": 7}),
        ("Predictions", "GET", "/predictions", None),
    ]

    for label, method, path, payload in steps:
        try:
            result = call(args.api, method, path, payload)
        except urllib.error.URLError as exc:
            raise SystemExit(f"{label} failed: {exc}") from exc
        print(f"\n== {label} ==")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
