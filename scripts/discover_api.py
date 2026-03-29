#!/usr/bin/env python3
"""
Discover Naver Smart Store seller center API endpoints.
Read-only GET requests only.
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
    # Set cookies
    for name, value in sess_data.get("cookies", {}).items():
        s.cookies.set(name, value, domain=".smartstore.naver.com")
        s.cookies.set(name, value, domain="sell.smartstore.naver.com")
    # Also set on naver.com domain for NID cookies
    for name, value in sess_data.get("cookies", {}).items():
        if name.startswith("NID") or name.startswith("NNB") or name.startswith("nid"):
            s.cookies.set(name, value, domain=".naver.com")
    # Set headers
    hdrs = sess_data.get("headers", {})
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": hdrs.get("Referer", "https://sell.smartstore.naver.com/"),
    })
    return s

def try_endpoint(s, url, label=None):
    """Try a GET request and report results."""
    label = label or url
    try:
        r = s.get(url, timeout=15, allow_redirects=False)
        status = r.status_code
        ct = r.headers.get("Content-Type", "")
        body = r.text[:800] if r.text else "(empty)"

        indicator = "OK" if status == 200 else ("REDIRECT" if 300 <= status < 400 else "FAIL")
        print(f"\n{'='*80}")
        print(f"[{indicator}] {status} - {label}")
        print(f"  URL: {url}")
        print(f"  Content-Type: {ct}")
        if 300 <= status < 400:
            print(f"  Location: {r.headers.get('Location', 'N/A')}")
        print(f"  Body preview: {body[:500]}")
        print(f"{'='*80}")
        return status, ct, r.text
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None, None

def extract_urls_from_html(html):
    """Extract potential API URLs from HTML/JS content."""
    patterns = [
        r'https?://[a-zA-Z0-9._/-]+(?:api|Api|API)[a-zA-Z0-9._/-]*',
        r'https?://sell\.smartstore\.naver\.com/[a-zA-Z0-9._/-]+',
        r'https?://[a-zA-Z0-9._/-]*naver\.com/[a-zA-Z0-9._/-]+',
        r'"(/o/[^"]+)"',
        r'"(/api/[^"]+)"',
        r'"(/seller/[^"]+)"',
        r'"(/v[0-9]+/[^"]+)"',
        r'"(/n/[^"]+)"',
        r'(?:baseUrl|apiUrl|endpoint|BASE_URL|API_URL)\s*[:=]\s*["\']([^"\']+)["\']',
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.\w+\(["\']([^"\']+)["\']',
        r'url\s*:\s*["\']([^"\']+)["\']',
    ]
    urls = set()
    for p in patterns:
        for m in re.findall(p, html):
            urls.add(m)
    return urls

def extract_js_urls(html):
    """Extract JavaScript file URLs from HTML."""
    patterns = [
        r'<script[^>]+src=["\']([^"\']+)["\']',
        r'<link[^>]+href=["\']([^"\']+\.js[^"\']*)["\']',
    ]
    urls = set()
    for p in patterns:
        for m in re.findall(p, html):
            urls.add(m)
    return urls

def main():
    print("Loading session...")
    sess_data = load_session()
    s = make_session(sess_data)

    # ========== PHASE 1: Fetch main page HTML ==========
    print("\n" + "#"*80)
    print("# PHASE 1: Fetch main page and analyze HTML")
    print("#"*80)

    status, ct, main_html = try_endpoint(s, f"{BASE}/", "Main page")

    if main_html and status == 200:
        # Extract URLs
        found_urls = extract_urls_from_html(main_html)
        js_urls = extract_js_urls(main_html)

        print(f"\n--- Found {len(found_urls)} potential API URLs in main page ---")
        for u in sorted(found_urls):
            print(f"  {u}")

        print(f"\n--- Found {len(js_urls)} JS files in main page ---")
        for u in sorted(js_urls):
            print(f"  {u}")

    # ========== PHASE 2: Try the home/about page ==========
    print("\n" + "#"*80)
    print("# PHASE 2: Try common pages")
    print("#"*80)

    pages = [
        f"{BASE}/home/about",
        f"{BASE}/home/dashboard",
        f"{BASE}/home",
        f"{BASE}/seller",
    ]
    for url in pages:
        try_endpoint(s, url, url.replace(BASE, ""))

    # ========== PHASE 3: Try known API patterns ==========
    print("\n" + "#"*80)
    print("# PHASE 3: Try known Naver Commerce API patterns")
    print("#"*80)

    api_endpoints = [
        # /o/seller patterns (common in Naver commerce)
        f"{BASE}/o/seller/sale/product/list",
        f"{BASE}/o/seller/sale/product",
        f"{BASE}/o/seller/sale/order/list",
        f"{BASE}/o/seller/sale/order",
        f"{BASE}/o/seller/home/about",
        f"{BASE}/o/seller/home/dashboard",
        f"{BASE}/o/seller/statistics/daily",
        f"{BASE}/o/seller/statistics",
        f"{BASE}/o/seller/settlement/list",
        f"{BASE}/o/seller/inquiry/list",
        f"{BASE}/o/seller/review/list",

        # /o/v2 patterns
        f"{BASE}/o/v2/seller/sale/product/list",
        f"{BASE}/o/v2/seller/sale/order/list",

        # /api patterns
        f"{BASE}/api/products",
        f"{BASE}/api/orders",
        f"{BASE}/api/seller",
        f"{BASE}/api/seller/info",
        f"{BASE}/api/dashboard",

        # /n/ patterns
        f"{BASE}/n/sale/product/list",
        f"{BASE}/n/sale/order/list",
        f"{BASE}/n/statistics/daily",

        # Direct Naver Commerce API
        "https://commerce.naver.com/api/seller",
        "https://commerce.naver.com/api/products",
        "https://center.sell.smartstore.naver.com/",
    ]

    for url in api_endpoints:
        try_endpoint(s, url)

    # ========== PHASE 4: Analyze JS bundles for API paths ==========
    print("\n" + "#"*80)
    print("# PHASE 4: Analyze JS bundles for API endpoint patterns")
    print("#"*80)

    if main_html and status == 200:
        # Pick up to 3 JS files to analyze
        js_to_check = []
        for u in js_urls:
            if not u.startswith("http"):
                u = BASE + u if u.startswith("/") else f"{BASE}/{u}"
            js_to_check.append(u)

        # Focus on main/app bundles first
        priority_js = [u for u in js_to_check if any(k in u.lower() for k in ["main", "app", "chunk", "vendor", "common"])]
        other_js = [u for u in js_to_check if u not in priority_js]

        to_analyze = (priority_js[:5] + other_js[:2])

        print(f"Analyzing {len(to_analyze)} JS files for API patterns...")

        for js_url in to_analyze:
            try:
                r = s.get(js_url, timeout=15)
                if r.status_code == 200 and r.text:
                    js_content = r.text
                    print(f"\n--- JS: {js_url} ({len(js_content)} chars) ---")

                    # Look for API endpoint patterns in JS
                    api_patterns = [
                        r'["\'](?:/o/[a-zA-Z0-9/_-]+)["\']',
                        r'["\'](?:/api/[a-zA-Z0-9/_-]+)["\']',
                        r'["\'](?:/n/[a-zA-Z0-9/_-]+)["\']',
                        r'["\'](?:/seller/[a-zA-Z0-9/_-]+)["\']',
                        r'["\'](?:/v[0-9]/[a-zA-Z0-9/_-]+)["\']',
                        r'baseURL\s*[:=]\s*["\']([^"\']+)["\']',
                        r'BASE_URL\s*[:=]\s*["\']([^"\']+)["\']',
                        r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
                        r'endpoint\s*[:=]\s*["\']([^"\']+)["\']',
                        r'["\']https?://[^"\']*(?:api|commerce|sell)[^"\']*["\']',
                    ]

                    found_in_js = set()
                    for p in api_patterns:
                        for m in re.findall(p, js_content):
                            # Clean up quotes
                            m = m.strip("\"'")
                            if len(m) > 3 and not m.endswith(('.js', '.css', '.png', '.svg', '.ico', '.woff', '.woff2')):
                                found_in_js.add(m)

                    if found_in_js:
                        print(f"  Found {len(found_in_js)} API-like paths:")
                        for path in sorted(found_in_js):
                            print(f"    {path}")
                    else:
                        print("  No API paths found in this file.")
            except Exception as e:
                print(f"  Error fetching {js_url}: {e}")

    # ========== PHASE 5: Try seller center iframe/SPA patterns ==========
    print("\n" + "#"*80)
    print("# PHASE 5: Try SPA / iframe / internal API patterns")
    print("#"*80)

    spa_endpoints = [
        # Common SPA routes that might return JSON when Accept: application/json
        f"{BASE}/home/seller-info",
        f"{BASE}/home/seller/info",
        f"{BASE}/o/home",
        f"{BASE}/o/home/about",
        f"{BASE}/o/home/seller",
        f"{BASE}/o/seller/info",

        # Panel-like APIs
        f"{BASE}/o/seller/panel/product",
        f"{BASE}/o/seller/panel/order",
        f"{BASE}/o/seller/panel/dashboard",

        # Search for GraphQL endpoint
        f"{BASE}/graphql",
        f"{BASE}/api/graphql",
    ]

    for url in spa_endpoints:
        try_endpoint(s, url)

    # ========== PHASE 6: Check Naver Commerce Platform API ==========
    print("\n" + "#"*80)
    print("# PHASE 6: Naver Commerce Platform API patterns")
    print("#"*80)

    commerce_endpoints = [
        "https://api.commerce.naver.com/external/v1/seller",
        "https://api.commerce.naver.com/external/v2/products",
        "https://sell.smartstore.naver.com/o/seller/sale/delivery",
        "https://sell.smartstore.naver.com/o/seller/sale/claim",
        "https://sell.smartstore.naver.com/o/seller/sale/cancel",
        "https://sell.smartstore.naver.com/o/notification",
        "https://sell.smartstore.naver.com/o/notify",
    ]

    for url in commerce_endpoints:
        try_endpoint(s, url)

    # ========== PHASE 7: Look for XHR patterns in the main HTML more carefully ==========
    print("\n" + "#"*80)
    print("# PHASE 7: Deep HTML analysis")
    print("#"*80)

    if main_html:
        # Look for inline scripts with data
        inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', main_html, re.DOTALL)
        print(f"Found {len(inline_scripts)} inline scripts")

        for i, script in enumerate(inline_scripts):
            if len(script.strip()) > 10:
                print(f"\n--- Inline script #{i+1} ({len(script)} chars) ---")
                # Show first 1000 chars of non-trivial scripts
                preview = script.strip()[:1000]
                print(preview)

                # Look for URLs, config objects
                config_patterns = [
                    r'window\.__[A-Z_]+__\s*=\s*(\{[^}]+\})',
                    r'window\.([A-Z_]+)\s*=',
                    r'"(https?://[^"]+)"',
                    r"'(https?://[^']+)'",
                ]
                for p in config_patterns:
                    for m in re.findall(p, script):
                        print(f"  Config/URL found: {m[:200]}")

        # Look for meta tags
        meta_tags = re.findall(r'<meta[^>]+>', main_html)
        print(f"\n--- Meta tags ({len(meta_tags)}) ---")
        for m in meta_tags:
            print(f"  {m}")

    print("\n\nDone!")

if __name__ == "__main__":
    main()
