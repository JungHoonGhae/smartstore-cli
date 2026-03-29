#!/usr/bin/env python3
"""
Final targeted tests using discovered patterns:
- NSI cookie → X-NCP-LOGIN-INFO header
- loginInfoService provides channelNo context
- Correct param names from $resource definitions
"""

import json
import re
import sys
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"
CHANNEL_NO = 1100114368
ACCOUNT_NO = 1100112229
REPRESENT_NO = 1100110443

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

def try_get(s, url, label=None, max_body=3000, extra_headers=None):
    label = label or url
    try:
        r = s.get(url, timeout=15, allow_redirects=True, headers=extra_headers)
        status = r.status_code
        ct = r.headers.get("Content-Type", "")
        is_json = "json" in ct.lower()
        indicator = "OK" if status == 200 else f"HTTP {status}"
        print(f"\n{'='*100}")
        print(f"[{indicator}] {label}")
        print(f"  Status: {status} | CT: {ct}")
        if is_json:
            try:
                parsed = json.loads(r.text)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                print(f"  JSON ({len(r.text)} bytes):")
                print(f"  {pretty[:max_body]}")
            except:
                print(f"  Raw: {r.text[:max_body]}")
        else:
            print(f"  Body: {r.text[:500]}")
        return status, ct, r.text
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None, None

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # First let's extract the interceptor logic more precisely
    print("="*100)
    print("STEP 0: Extract exact interceptor and loginInfoService logic")
    print("="*100)

    r = s.get(f"{BASE}/app.js?f3dfd2e83632f6ec00be", timeout=30)
    app_js = r.text

    # Find the httpInterceptorService factory function
    idx = app_js.find('"httpInterceptorService"')
    if idx < 0:
        idx = app_js.find("httpInterceptorService")
    # Find the function that defines it
    # Look for the module number that exports it
    for match in re.finditer(r'service\("httpInterceptorService"\s*,\s*n\((\d+)\)\)', app_js):
        module_num = match.group(1)
        print(f"httpInterceptorService is in module {module_num}")
        # Find the module definition
        # webpack modules are indexed, skip direct extraction
        break

    # Find loginInfoService
    for match in re.finditer(r'service\("loginInfoService"\s*,\s*n\((\d+)\)\)', app_js):
        module_num = match.group(1)
        print(f"loginInfoService is in module {module_num}")
        break

    # Let's extract around the httpInterceptorService function - look for request interceptor
    interceptor_matches = re.findall(r'httpInterceptorService[^}]*\{[^}]*request\s*:\s*function[^}]*\{[^}]{0,2000}', app_js)
    if not interceptor_matches:
        # Try different pattern - the interceptor config
        interceptor_matches = re.findall(r'request\s*:\s*function\s*\([^)]*\)\s*\{[^}]{0,500}loginInfo[^}]{0,500}', app_js)

    if interceptor_matches:
        for m in interceptor_matches[:3]:
            print(f"\nInterceptor request function:\n  {m[:1000]}")

    # Find how X-NCP-LOGIN-INFO is constructed
    ncp_login_info_patterns = re.findall(r'X-NCP-LOGIN-INFO[^;]{0,500}', app_js)
    for p in ncp_login_info_patterns[:5]:
        print(f"\nX-NCP-LOGIN-INFO usage: {p[:500]}")

    # Also search for how loginInfoService constructs the value
    login_info_construct = re.findall(r'loginInfo[^;]{0,300}stringify[^;]{0,200}', app_js)
    for p in login_info_construct[:5]:
        print(f"\nloginInfo stringify: {p[:500]}")

    # ===== STEP 1: Try with proper X-NCP-LOGIN-INFO header =====
    print("\n\n" + "="*100)
    print("STEP 1: Try endpoints with proper X-NCP-LOGIN-INFO JSON header")
    print("="*100)

    # The login/channels response gave us all the info we need
    login_info = {
        "channelNo": CHANNEL_NO,
        "accountNo": ACCOUNT_NO,
        "representNo": REPRESENT_NO,
        "channelName": "hellodev",
        "type": "STOREFARM"
    }

    auth_headers = {
        "X-NCP-LOGIN-INFO": json.dumps(login_info, separators=(',', ':')),
    }

    # Test core endpoints
    endpoints = [
        (f"{BASE}/api/seller/info", "seller/info"),
        (f"{BASE}/api/sellers", "sellers"),
        (f"{BASE}/api/v1/sellers", "v1/sellers"),
        (f"{BASE}/api/myconfigs", "myconfigs"),
        (f"{BASE}/api/channels", "channels"),
        (f"{BASE}/api/products/list", "products/list"),
        (f"{BASE}/api/channel-products/list", "channel-products/list"),
        (f"{BASE}/api/dashboards/modals", "dashboards/modals"),
        (f"{BASE}/api/sales-day/with-from-to?fromDateString={month_ago}&toDateString={today}", "sales-day/with-from-to"),
        (f"{BASE}/api/sale-summaries", "sale-summaries"),
        (f"{BASE}/api/settlements", "settlements"),
        (f"{BASE}/api/v3/contents/reviews/search", "reviews/search"),
        (f"{BASE}/api/product/delivery/companies", "delivery companies"),
        (f"{BASE}/api/seller/notification", "notifications"),
        (f"{BASE}/api/categories", "categories"),
        (f"{BASE}/api/delivery-bundle-groups", "delivery-bundle-groups"),
    ]

    for url, label in endpoints:
        try_get(s, url, f"{label} with X-NCP-LOGIN-INFO", extra_headers=auth_headers)

    # ===== STEP 2: Also try with both channelNo param AND header =====
    print("\n\n" + "="*100)
    print("STEP 2: Try with BOTH channelNo param AND X-NCP-LOGIN-INFO header")
    print("="*100)

    endpoints2 = [
        (f"{BASE}/api/seller/info?channelNo={CHANNEL_NO}", "seller/info"),
        (f"{BASE}/api/sellers?channelNo={CHANNEL_NO}", "sellers"),
        (f"{BASE}/api/v1/sellers?channelNo={CHANNEL_NO}", "v1/sellers"),
        (f"{BASE}/api/myconfigs?channelNo={CHANNEL_NO}", "myconfigs"),
        (f"{BASE}/api/products/list?channelNo={CHANNEL_NO}", "products/list"),
        (f"{BASE}/api/channel-products/list?channelNo={CHANNEL_NO}", "channel-products/list"),
        (f"{BASE}/api/dashboards/modals?channelNo={CHANNEL_NO}", "dashboards/modals"),
        (f"{BASE}/api/sales-day/with-from-to?channelNo={CHANNEL_NO}&fromDateString={month_ago}&toDateString={today}", "sales-day/with-from-to"),
        (f"{BASE}/api/categories?channelNo={CHANNEL_NO}", "categories"),
    ]

    for url, label in endpoints2:
        try_get(s, url, f"{label} with param+header", extra_headers=auth_headers)

    # ===== STEP 3: Try seller/info with ssnShow =====
    print("\n\n" + "="*100)
    print("STEP 3: Try seller/info with known params")
    print("="*100)

    try_get(s, f"{BASE}/api/seller/info?ssnShow=true", "seller/info?ssnShow=true", extra_headers=auth_headers)
    try_get(s, f"{BASE}/api/seller/info?ssnShow=true&channelNo={CHANNEL_NO}", "seller/info?ssnShow=true&channelNo", extra_headers=auth_headers)

    print("\n\nDone!")

if __name__ == "__main__":
    main()
