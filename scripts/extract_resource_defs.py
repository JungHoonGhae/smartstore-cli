#!/usr/bin/env python3
"""
Extract the exact $resource definitions for key API endpoints from app.js.
Find what parameters each endpoint requires.
"""

import json
import re
import sys
import warnings

warnings.filterwarnings("ignore")

import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"

def load_session():
    with open(SESSION_PATH) as f:
        return json.load(f)

def make_session(sess_data):
    s = requests.Session()
    for name, value in sess_data.get("cookies", {}).items():
        s.cookies.set(name, value, domain="sell.smartstore.naver.com", path="/")
    for name, value in sess_data.get("cookies", {}).items():
        if name.startswith("NID") or name.startswith("NNB") or name.startswith("nid") or name.startswith("SRT") or name == "BUC" or name.startswith("NAC"):
            s.cookies.set(name, value, domain=".naver.com", path="/")
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://sell.smartstore.naver.com/",
    })
    return s

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    r = s.get(f"{BASE}/app.js?f3dfd2e83632f6ec00be", timeout=30)
    app_js = r.text
    print(f"app.js loaded: {len(app_js)} chars")

    # We need to find the resource/service definitions for key endpoints
    # In AngularJS $resource, the pattern is:
    # $resource("/api/xxx", {param1: "@param1"}, { action: {method: "GET", params: {...}} })

    # Extract wider context around each key endpoint
    key_endpoints = [
        "/api/products/list",
        "/api/channel-products/list",
        "/api/seller/info",
        "/api/sellers",
        "/api/myconfigs",
        "/api/dashboards",
        "/api/sales-day",
        "/api/sale-summaries",
        "/api/settlements",
        "/api/categories",
        "/api/delivery-bundle-groups",
        "/api/credit/history",
        "/api/penalty",
        "/api/v3/contents/reviews",
        "/api/channels",
        "/api/v1/sellers",
        "/api/shared/talktalk",
    ]

    for endpoint in key_endpoints:
        # Find all occurrences
        idx = 0
        occurrences = []
        while True:
            idx = app_js.find(endpoint, idx)
            if idx < 0:
                break
            # Get 500 chars before and 500 chars after
            start = max(0, idx - 200)
            end = min(len(app_js), idx + 500)
            chunk = app_js[start:end]
            occurrences.append(chunk)
            idx += 1

        print(f"\n{'='*100}")
        print(f"ENDPOINT: {endpoint} ({len(occurrences)} occurrences)")
        print(f"{'='*100}")

        for i, occ in enumerate(occurrences[:3]):
            print(f"\n  --- Occurrence {i+1} ---")
            print(f"  {occ}")

    # Also find CSRF / XSRF patterns
    print(f"\n{'='*100}")
    print(f"CSRF / XSRF PATTERNS")
    print(f"{'='*100}")

    csrf_patterns = [
        r'csrf[^;]{0,200}',
        r'xsrf[^;]{0,200}',
        r'_token[^;]{0,200}',
        r'anti-forgery[^;]{0,200}',
    ]
    for pattern in csrf_patterns:
        matches = re.findall(pattern, app_js, re.IGNORECASE)
        if matches:
            for m in set(list(matches)[:5]):
                print(f"  {m[:200]}")

    # Also look for how login/init is called (the one that seems to bootstrap things)
    print(f"\n{'='*100}")
    print(f"LOGIN/INIT CALL PATTERN")
    print(f"{'='*100}")

    idx = 0
    while True:
        idx = app_js.find("/api/login/init", idx)
        if idx < 0:
            break
        start = max(0, idx - 300)
        end = min(len(app_js), idx + 500)
        print(f"\n  {app_js[start:end]}")
        idx += 1

    print("\n\nDone!")

if __name__ == "__main__":
    main()
