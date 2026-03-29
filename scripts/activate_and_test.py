#!/usr/bin/env python3
"""
Activate the channel via POST /api/login/change-channel, then test all GET endpoints.
The change-channel POST is read-safe (it just selects which store to view).
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
ROLE_NO = 200206319

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
    hdrs = sess_data.get("headers", {})
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": hdrs.get("Referer", "https://sell.smartstore.naver.com/"),
        "Origin": "https://sell.smartstore.naver.com",
    })
    return s

def try_get(s, url, label=None, max_body=3000):
    label = label or url
    try:
        r = s.get(url, timeout=15, allow_redirects=True)
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
                if len(pretty) > max_body:
                    print(f"  ... (truncated)")
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
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # ===== Step 1: POST to change-channel =====
    print("="*100)
    print("STEP 1: POST /api/login/change-channel to activate channel")
    print("="*100)

    # From app.js: change-channel params: {roleNo:"@roleNo",channelNo:"@channelNo",url:"@url"}
    change_url = f"{BASE}/api/login/change-channel?roleNo={ROLE_NO}&channelNo={CHANNEL_NO}&url=%2F"
    print(f"POST {change_url}")

    try:
        r = s.post(change_url, timeout=15, allow_redirects=False)
        print(f"  Status: {r.status_code}")
        print(f"  CT: {r.headers.get('Content-Type', '')}")
        print(f"  Body: {r.text[:1000]}")
        print(f"  Location: {r.headers.get('Location', 'N/A')}")
        for k, v in r.headers.items():
            if k.lower() in ('set-cookie', 'x-ses-valid', 'location'):
                print(f"  Header {k}: {v[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

    # ===== Step 2: Now test all GET endpoints =====
    print("\n\n" + "="*100)
    print("STEP 2: Test GET endpoints after channel activation")
    print("="*100)

    # Core seller info
    try_get(s, f"{BASE}/api/seller/info", "seller/info")
    try_get(s, f"{BASE}/api/seller/info?ssnShow=true", "seller/info?ssnShow=true")
    try_get(s, f"{BASE}/api/sellers", "sellers")
    try_get(s, f"{BASE}/api/v1/sellers", "v1/sellers")
    try_get(s, f"{BASE}/api/myconfigs", "myconfigs")
    try_get(s, f"{BASE}/api/channels", "channels")
    try_get(s, f"{BASE}/api/seller-configs/", "seller-configs")

    # Products
    try_get(s, f"{BASE}/api/products/list", "products/list")
    try_get(s, f"{BASE}/api/channel-products/list", "channel-products/list")
    try_get(s, f"{BASE}/api/channel-products/list/search", "channel-products/list/search")
    try_get(s, f"{BASE}/api/categories", "categories")

    # Dashboard
    try_get(s, f"{BASE}/api/dashboards/", "dashboards")
    try_get(s, f"{BASE}/api/dashboards/modals", "dashboards/modals")

    # Sales/Stats
    try_get(s, f"{BASE}/api/sales-day/", "sales-day")
    try_get(s, f"{BASE}/api/sales-day/with-from-to?fromDateString={month_ago}&toDateString={today}", "sales-day/with-from-to")
    try_get(s, f"{BASE}/api/sale-summaries", "sale-summaries")

    # Settlements
    try_get(s, f"{BASE}/api/settlements", "settlements")

    # Reviews
    try_get(s, f"{BASE}/api/v3/contents/reviews/search", "reviews/search")
    try_get(s, f"{BASE}/api/v3/contents/reviews/dash-board/review-count", "reviews/dash-board/review-count")
    try_get(s, f"{BASE}/api/v3/contents/reviews/dash-board/low-score", "reviews/dash-board/low-score")

    # Notifications
    try_get(s, f"{BASE}/api/seller/notification", "seller/notification")

    # Delivery
    try_get(s, f"{BASE}/api/product/delivery/companies", "delivery/companies")
    try_get(s, f"{BASE}/api/delivery-bundle-groups", "delivery-bundle-groups")

    # TalkTalk / inquiries
    try_get(s, f"{BASE}/api/seller/talktalk", "seller/talktalk")
    try_get(s, f"{BASE}/api/shared/talktalk", "shared/talktalk")

    # Grade
    try_get(s, f"{BASE}/api/seller/grade/raw-data", "seller/grade/raw-data")
    try_get(s, f"{BASE}/api/sellers/growth-mileage", "sellers/growth-mileage")

    # Credit/Penalty
    try_get(s, f"{BASE}/api/credit/history", "credit/history")
    try_get(s, f"{BASE}/api/penalty", "penalty")

    # Service control
    try_get(s, f"{BASE}/api/service-open-control/", "service-open-control")

    # Seller info additional
    try_get(s, f"{BASE}/api/seller/info/modHistory", "seller/info/modHistory")
    try_get(s, f"{BASE}/api/seller/notification", "seller/notification")
    try_get(s, f"{BASE}/api/v2/data-statistics/search-inflow/channel-products", "v2/data-statistics/search-inflow")

    # Agency
    try_get(s, f"{BASE}/api/agency/getUseAgencies", "agency/getUseAgencies")

    # Interlock
    try_get(s, f"{BASE}/api/interlock", "interlock")

    # Lounge
    try_get(s, f"{BASE}/api/lounge", "lounge")

    # Check/Account
    try_get(s, f"{BASE}/api/check/account", "check/account")

    # BizAdvisor token
    try_get(s, f"{BASE}/api/bizadvisor/createToken", "bizadvisor/createToken")

    # Login context
    try_get(s, f"{BASE}/api/login/channels", "login/channels")
    try_get(s, f"{BASE}/api/context", "context (trimmed)", max_body=500)

    print("\n\n" + "="*100)
    print("TESTING COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()
