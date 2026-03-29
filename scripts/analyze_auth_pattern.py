#!/usr/bin/env python3
"""
Deeper analysis: find how the AngularJS app passes authentication context.
Look for channelNo header patterns, cookie patterns, and interceptors.
Also try the /o/v3/ pattern JS bundles to find XHR API calls.
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
        print(f"\n{'='*100}")
        print(f"[{indicator}] {label}")
        print(f"  Status: {status} | Content-Type: {ct}")
        if is_json:
            try:
                parsed = json.loads(r.text)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                print(f"  JSON ({len(r.text)} bytes): {pretty[:max_body]}")
            except:
                print(f"  Body: {r.text[:max_body]}")
        else:
            print(f"  Body: {r.text[:500]}")
        return status, ct, r.text
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None, None

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    # Phase 1: Search app.js for how channelNo is passed
    print("="*100)
    print("PHASE 1: Analyze app.js for channelNo / authentication patterns")
    print("="*100)

    r = s.get(f"{BASE}/app.js?f3dfd2e83632f6ec00be", timeout=30)
    app_js = r.text

    # Look for how channelNo gets injected
    patterns_to_search = [
        (r'channelNo["\'\s]*[:=][^,;\n]{0,200}', "channelNo assignment"),
        (r'["\']channelNo["\']\s*[:]\s*[^,}\n]{0,100}', "channelNo in object"),
        (r'headers\s*\[\s*["\'][^"\']*["\']', "header setting"),
        (r'setRequestHeader\s*\([^)]+\)', "XHR header setting"),
        (r'interceptor[^{]*\{[^}]{0,500}', "interceptor pattern"),
        (r'X-[A-Z][-A-Za-z]+', "custom X- headers"),
        (r'x-sell[^"\']*', "x-sell headers"),
        (r'sell-[a-z-]+', "sell- patterns"),
        (r'["\']x-[^"\']+["\']', "any x- header references"),
    ]

    for pattern, desc in patterns_to_search:
        matches = re.findall(pattern, app_js, re.IGNORECASE)
        unique_matches = list(set(matches))
        if unique_matches:
            print(f"\n--- {desc} ({len(unique_matches)} unique matches) ---")
            for m in sorted(unique_matches)[:30]:
                print(f"  {m[:200]}")

    # Look for how the session/auth header is constructed
    print("\n\n--- Looking for auth/session header construction ---")
    auth_patterns = [
        r'(?:Authorization|authorization)\s*[:=]\s*[^,;\n]{0,200}',
        r'(?:token|Token|TOKEN)\s*[:=]\s*[^,;\n]{0,200}',
        r'withCredentials\s*[:=]\s*true',
        r'xsrfCookieName\s*[:=]\s*[^,;\n]{0,100}',
        r'xsrfHeaderName\s*[:=]\s*[^,;\n]{0,100}',
    ]
    for pattern in auth_patterns:
        matches = re.findall(pattern, app_js)
        if matches:
            for m in set(matches):
                print(f"  {m[:200]}")

    # Phase 2: Look for how the SPA constructs API URLs
    print("\n\n" + "="*100)
    print("PHASE 2: Analyze how the SPA builds API URLs")
    print("="*100)

    # Look for $http or fetch patterns near /api/ calls
    api_call_patterns = [
        r'\.get\(\s*["\'][^"\']*(?:products|channel-products)[^"\']*["\']\s*(?:,\s*\{[^}]{0,300}\})?',
        r'\.get\(\s*["\'][^"\']*(?:sales-day|sale-summaries|settlements)[^"\']*["\']\s*(?:,\s*\{[^}]{0,300}\})?',
        r'\.get\(\s*["\'][^"\']*(?:seller/info|sellers|myconfigs)[^"\']*["\']\s*(?:,\s*\{[^}]{0,300}\})?',
        r'\.get\(\s*["\'][^"\']*(?:dashboards|reviews)[^"\']*["\']\s*(?:,\s*\{[^}]{0,300}\})?',
    ]
    for pattern in api_call_patterns:
        matches = re.findall(pattern, app_js)
        if matches:
            print(f"\n--- API call pattern ---")
            for m in matches[:10]:
                print(f"  {m[:300]}")

    # Phase 3: Try with cookie-based channel selection
    print("\n\n" + "="*100)
    print("PHASE 3: Try endpoints with cookie-based channel (NNB cookie approach)")
    print("="*100)

    # The SPA might use an interceptor that reads channelNo from state/cookie
    # Let's try passing channelNo as an HTTP header
    headers_to_try = [
        {"x-sell-channel-no": str(CHANNEL_NO)},
        {"X-Channel-No": str(CHANNEL_NO)},
        {"channelNo": str(CHANNEL_NO)},
        {"x-ncp-channel": str(CHANNEL_NO)},
    ]

    for extra in headers_to_try:
        hdr_name = list(extra.keys())[0]
        status, ct, body = try_get(s, f"{BASE}/api/products/list?channelNo={CHANNEL_NO}",
                                    f"products/list with header {hdr_name}={CHANNEL_NO}", extra_headers=extra)
        if status == 200:
            print(f"  *** SUCCESS with header {hdr_name} ***")
            break

    # Phase 4: Deep dive into the /o/v3/ HTML pages to find their JS bundles
    print("\n\n" + "="*100)
    print("PHASE 4: Analyze /o/v3/ JS bundles for order API patterns")
    print("="*100)

    r = s.get(f"{BASE}/o/v3/order/summary", timeout=15)
    if r.status_code == 200:
        html = r.text

        # Find JS files
        js_files = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
        print(f"Found {len(js_files)} JS files in /o/v3/order/summary:")
        for js in js_files:
            print(f"  {js}")

        # Analyze first few JS files for API patterns
        for js_url in js_files[:5]:
            if not js_url.startswith("http"):
                js_url = BASE + (js_url if js_url.startswith("/") else f"/{js_url}")
            try:
                jr = s.get(js_url, timeout=15)
                if jr.status_code == 200:
                    js_text = jr.text

                    # Find API patterns
                    api_matches = set()
                    for p in [r'["\'](?:/api/[a-zA-Z0-9/_?&=-]+)["\']',
                              r'["\'](?:https?://[^"\']*(?:api|sell\.smartstore)[^"\']+)["\']']:
                        for m in re.findall(p, js_text):
                            m = m.strip("\"'")
                            if not m.endswith(('.js', '.css', '.png')):
                                api_matches.add(m)

                    if api_matches:
                        print(f"\n  JS: {js_url[:80]} -> {len(api_matches)} API paths:")
                        for m in sorted(api_matches):
                            print(f"    {m}")
            except:
                pass

    # Phase 5: Try the /o/v3/ API endpoints discovered or guessed
    print("\n\n" + "="*100)
    print("PHASE 5: Test /o/v3/ API endpoints")
    print("="*100)

    o_v3_endpoints = [
        f"{BASE}/o/v3/api/order/summary?channelNo={CHANNEL_NO}",
        f"{BASE}/o/v3/api/manage/order?channelNo={CHANNEL_NO}",
        f"{BASE}/o/v3/api/n/sale/delivery?channelNo={CHANNEL_NO}",
    ]
    for url in o_v3_endpoints:
        try_get(s, url)

    # Phase 6: Check if login/init with channelNo returns useful context
    print("\n\n" + "="*100)
    print("PHASE 6: Check login endpoints with channelNo")
    print("="*100)

    try_get(s, f"{BASE}/api/login/init?channelNo={CHANNEL_NO}", "login/init with channelNo")
    try_get(s, f"{BASE}/api/login/check?channelNo={CHANNEL_NO}", "login/check with channelNo")
    try_get(s, f"{BASE}/api/login/check-neoid-session", "login/check-neoid-session")

    print("\n\nDone!")

if __name__ == "__main__":
    main()
