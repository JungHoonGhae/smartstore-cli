#!/usr/bin/env python3
"""
Deep analysis:
1. Extract the httpInterceptorService from app.js to understand auth injection
2. Extract how products/list and channel-products/list are actually called
3. Try /api/meta/enums from v3 bundle
4. Examine common.bundle.js more carefully for GraphQL or REST patterns
"""

import json
import re
import sys
import warnings

warnings.filterwarnings("ignore")

import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"
CHANNEL_NO = 1100114368

def load_session():
    with open(SESSION_PATH) as f:
        return json.load(f)

def make_session(sess_data):
    s = requests.Session()
    for name, value in sess_data.get("cookies", {}).items():
        s.cookies.set(name, value, domain=".smartstore.naver.com")
        s.cookies.set(name, value, domain="sell.smartstore.naver.com")
    for name, value in sess_data.get("cookies", {}).items():
        if name.startswith("NID") or name.startswith("NNB") or name.startswith("nid"):
            s.cookies.set(name, value, domain=".naver.com")
    hdrs = sess_data.get("headers", {})
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": hdrs.get("Referer", "https://sell.smartstore.naver.com/"),
    })
    return s

def try_get(s, url, label=None, max_body=2000, extra_headers=None):
    label = label or url
    try:
        r = s.get(url, timeout=15, allow_redirects=True, headers=extra_headers)
        status = r.status_code
        ct = r.headers.get("Content-Type", "")
        is_json = "json" in ct.lower()
        indicator = "OK" if status == 200 else f"HTTP {status}"
        print(f"\n[{indicator}] {label}")
        print(f"  Status: {status} | CT: {ct}")
        if is_json:
            try:
                parsed = json.loads(r.text)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                print(f"  JSON ({len(r.text)} bytes): {pretty[:max_body]}")
            except:
                print(f"  Body: {r.text[:max_body]}")
        else:
            print(f"  Body ({len(r.text)} bytes): {r.text[:500]}")
        return status, ct, r.text
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None, None

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    # ===== Step 1: Extract interceptor from app.js =====
    print("="*100)
    print("STEP 1: Extract httpInterceptorService from app.js")
    print("="*100)

    r = s.get(f"{BASE}/app.js?f3dfd2e83632f6ec00be", timeout=30)
    app_js = r.text

    # Find the httpInterceptorService definition
    # Look for the module definition and the interceptor factory
    idx = app_js.find("httpInterceptorService")
    if idx >= 0:
        # Extract surrounding context (2000 chars around)
        start = max(0, idx - 500)
        end = min(len(app_js), idx + 3000)
        chunk = app_js[start:end]
        print(f"Found httpInterceptorService at position {idx}")
        print(f"Context:\n{chunk}")

    # Also find where the $resource / $http patterns are defined for products
    print("\n\n" + "="*100)
    print("STEP 2: Find $resource definitions for key APIs")
    print("="*100)

    # Find product resource definitions
    resource_patterns = [
        (r'products/list[^}]{0,500}', "products/list resource"),
        (r'channel-products/list[^}]{0,500}', "channel-products/list resource"),
        (r'sale-summaries[^}]{0,500}', "sale-summaries resource"),
        (r'sales-day[^}]{0,500}', "sales-day resource"),
        (r'settlements[^}]{0,1000}', "settlements resource"),
        (r'dashboards[^}]{0,500}', "dashboards resource"),
        (r'reviews/search[^}]{0,500}', "reviews/search resource"),
        (r'seller/info[^}]{0,500}', "seller/info resource"),
    ]

    for pattern, desc in resource_patterns:
        matches = re.findall(pattern, app_js, re.IGNORECASE)
        if matches:
            print(f"\n--- {desc} ({len(matches)} matches) ---")
            for m in matches[:3]:
                print(f"  {m[:500]}")
        else:
            print(f"\n--- {desc}: NO MATCHES ---")

    # ===== Step 3: Try /api/meta/enums =====
    print("\n\n" + "="*100)
    print("STEP 3: Test /api/meta/enums and other v3 endpoints")
    print("="*100)

    try_get(s, f"{BASE}/api/meta/enums", "api/meta/enums (from v3 bundle)")
    try_get(s, f"{BASE}/api/meta/enums?channelNo={CHANNEL_NO}", "api/meta/enums with channelNo")

    # ===== Step 4: Analyze common.bundle.js more deeply =====
    print("\n\n" + "="*100)
    print("STEP 4: Deep analysis of v3 common.bundle.js")
    print("="*100)

    r = s.get(f"{BASE}/o/v3/temp/static/npay/app/common.bundle.js?260318-210509", timeout=15)
    if r.status_code == 200:
        common_js = r.text
        print(f"common.bundle.js: {len(common_js)} chars")

        # Find all API path patterns
        all_paths = set()
        for p in [r'["\'](?:/api/[a-zA-Z0-9/_?&=.-]+)["\']',
                  r'["\'](?:/o/v3/[a-zA-Z0-9/_?&=.-]+)["\']',
                  r'["\'](?:/o/[a-zA-Z0-9/_?&=.-]+)["\']',
                  r'baseURL\s*[:=]\s*["\']([^"\']+)["\']']:
            for m in re.findall(p, common_js):
                m = m.strip("\"'")
                if not m.endswith(('.js', '.css', '.png', '.svg')):
                    all_paths.add(m)

        print(f"Found {len(all_paths)} paths:")
        for p in sorted(all_paths):
            print(f"  {p}")

        # Look for GraphQL patterns
        gql_patterns = re.findall(r'(?:query|mutation)\s+\w+[^}]{0,200}', common_js)
        if gql_patterns:
            print(f"\nGraphQL patterns found ({len(gql_patterns)}):")
            for g in gql_patterns[:10]:
                print(f"  {g[:200]}")
        else:
            print("\nNo GraphQL patterns found.")

        # Look for how requests are made (fetch, axios, etc)
        req_patterns = re.findall(r'(?:fetch|axios|XMLHttpRequest)\s*\([^)]{0,200}\)', common_js)
        if req_patterns:
            print(f"\nRequest patterns ({len(req_patterns)}):")
            for rp in req_patterns[:10]:
                print(f"  {rp[:200]}")

    # ===== Step 5: Analyze order.bundle.js =====
    print("\n\n" + "="*100)
    print("STEP 5: Deep analysis of v3 order.bundle.js")
    print("="*100)

    r = s.get(f"{BASE}/o/v3/temp/static/npay/app/order.bundle.js?260318-210509", timeout=15)
    if r.status_code == 200:
        order_js = r.text
        print(f"order.bundle.js: {len(order_js)} chars")

        all_paths = set()
        for p in [r'["\'](?:/api/[a-zA-Z0-9/_?&=.-]+)["\']',
                  r'["\'](?:/o/v3/[a-zA-Z0-9/_?&=.-]+)["\']',
                  r'["\'](?:/o/[a-zA-Z0-9/_?&=.-]+)["\']',
                  r'url\s*:\s*["\']([/][a-zA-Z0-9/_?&=.-]+)["\']']:
            for m in re.findall(p, order_js):
                m = m.strip("\"'")
                if not m.endswith(('.js', '.css', '.png', '.svg')):
                    all_paths.add(m)

        print(f"Found {len(all_paths)} paths:")
        for p in sorted(all_paths):
            print(f"  {p}")

        # Look for GraphQL
        gql_matches = re.findall(r'(?:query|mutation)\s*[({]\s*[^}]{0,200}', order_js)
        if gql_matches:
            print(f"\nGraphQL queries/mutations ({len(gql_matches)}):")
            for g in gql_matches[:20]:
                print(f"  {g[:300]}")

    # ===== Step 6: Look for the NSI token pattern more carefully =====
    print("\n\n" + "="*100)
    print("STEP 6: NSI token / session token pattern")
    print("="*100)

    # Extract the interceptor that adds NSI
    nsi_patterns = re.findall(r'NSI[^;]{0,300}', app_js)
    for p in nsi_patterns[:10]:
        print(f"  NSI pattern: {p[:300]}")

    # Also check X-Ses-Valid
    ses_patterns = re.findall(r'Ses-Valid[^;]{0,300}', app_js)
    for p in ses_patterns[:10]:
        print(f"  Ses-Valid pattern: {p[:300]}")

    # ===== Step 7: Try with X-Ses-Valid header =====
    print("\n\n" + "="*100)
    print("STEP 7: Try endpoints with X-Ses-Valid and X-NCP-LOGIN-INFO headers")
    print("="*100)

    nsi_token = sess_data["cookies"].get("NSI", "")
    print(f"NSI cookie value: {nsi_token}")

    test_headers = {
        "X-Ses-Valid": nsi_token,
        "X-NCP-LOGIN-INFO": json.dumps({"channelNo": CHANNEL_NO}),
    }
    try_get(s, f"{BASE}/api/products/list?channelNo={CHANNEL_NO}",
            "products/list with X-Ses-Valid + X-NCP-LOGIN-INFO", extra_headers=test_headers)

    test_headers2 = {
        "X-Ses-Valid": "true",
    }
    try_get(s, f"{BASE}/api/products/list?channelNo={CHANNEL_NO}",
            "products/list with X-Ses-Valid=true", extra_headers=test_headers2)

    # Try changing the channelNo cookie
    test_headers3 = {
        "Cookie": f"channelNo={CHANNEL_NO}",
    }
    try_get(s, f"{BASE}/api/products/list",
            "products/list with channelNo cookie", extra_headers=test_headers3)

    print("\n\nDone!")

if __name__ == "__main__":
    main()
