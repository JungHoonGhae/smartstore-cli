#!/usr/bin/env python3
"""
Test Naver Smart Store APIs with proper query parameters.
Uses channelNo discovered from api/login/channels.
Read-only GET requests only.
"""

import json
import sys
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"

# From api/login/channels response
CHANNEL_NO = 1100114368
ACCOUNT_NO = 1100112229

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

def try_get(s, url, label=None, max_body=2000):
    label = label or url
    try:
        r = s.get(url, timeout=15, allow_redirects=True)
        status = r.status_code
        ct = r.headers.get("Content-Type", "")
        is_json = "json" in ct.lower()
        indicator = "OK" if status == 200 else f"HTTP {status}"

        print(f"\n{'='*100}")
        print(f"[{indicator}] {label}")
        print(f"  URL: {url}")
        print(f"  Status: {status} | Content-Type: {ct}")

        if is_json:
            try:
                parsed = json.loads(r.text)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                print(f"  JSON Response ({len(r.text)} bytes):")
                print(f"  {pretty[:max_body]}")
                if len(pretty) > max_body:
                    print(f"  ... (truncated, total {len(pretty)} chars)")
            except:
                print(f"  Body: {r.text[:max_body]}")
        else:
            print(f"  Body: {r.text[:500]}")

        return status, ct, r.text, is_json
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None, None, False

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    this_month = datetime.now().strftime("%Y-%m")

    print("="*100)
    print(f"TESTING APIs WITH channelNo={CHANNEL_NO}, accountNo={ACCOUNT_NO}")
    print("="*100)

    # ===== SELLER INFO WITH PARAMS =====
    print("\n\n### SELLER INFO ###")
    try_get(s, f"{BASE}/api/seller/info?channelNo={CHANNEL_NO}", "seller/info with channelNo")
    try_get(s, f"{BASE}/api/sellers?channelNo={CHANNEL_NO}", "sellers with channelNo")
    try_get(s, f"{BASE}/api/v1/sellers?channelNo={CHANNEL_NO}", "v1/sellers with channelNo")
    try_get(s, f"{BASE}/api/channels?channelNo={CHANNEL_NO}", "channels with channelNo")
    try_get(s, f"{BASE}/api/myconfigs?channelNo={CHANNEL_NO}", "myconfigs with channelNo")
    try_get(s, f"{BASE}/api/seller-configs/?channelNo={CHANNEL_NO}", "seller-configs with channelNo")

    # ===== PRODUCTS WITH PARAMS =====
    print("\n\n### PRODUCTS ###")
    try_get(s, f"{BASE}/api/products?channelNo={CHANNEL_NO}", "products with channelNo")
    try_get(s, f"{BASE}/api/products/list?channelNo={CHANNEL_NO}", "products/list with channelNo")
    try_get(s, f"{BASE}/api/products/list/search?channelNo={CHANNEL_NO}", "products/list/search with channelNo")
    try_get(s, f"{BASE}/api/channel-products/list?channelNo={CHANNEL_NO}", "channel-products/list with channelNo")
    try_get(s, f"{BASE}/api/channel-products/list/search?channelNo={CHANNEL_NO}", "channel-products/list/search with channelNo")
    try_get(s, f"{BASE}/api/channel-products/list?channelNo={CHANNEL_NO}&page=1&size=10", "channel-products/list with page params")

    # ===== DASHBOARDS WITH PARAMS =====
    print("\n\n### DASHBOARDS ###")
    try_get(s, f"{BASE}/api/dashboards/?channelNo={CHANNEL_NO}", "dashboards with channelNo")
    try_get(s, f"{BASE}/api/dashboards/modals?channelNo={CHANNEL_NO}", "dashboards/modals with channelNo")

    # ===== SALES / STATS WITH PARAMS =====
    print("\n\n### SALES & STATS ###")
    try_get(s, f"{BASE}/api/sales-day/?channelNo={CHANNEL_NO}", "sales-day with channelNo")
    try_get(s, f"{BASE}/api/sales-day/?channelNo={CHANNEL_NO}&date={today}", "sales-day with date")
    try_get(s, f"{BASE}/api/sales-day/with-from-to?channelNo={CHANNEL_NO}&from={month_ago}&to={today}", "sales-day/with-from-to with date range")
    try_get(s, f"{BASE}/api/sale-summaries?channelNo={CHANNEL_NO}", "sale-summaries with channelNo")
    try_get(s, f"{BASE}/api/sale-summaries?channelNo={CHANNEL_NO}&from={month_ago}&to={today}", "sale-summaries with dates")

    # ===== REVIEWS WITH PARAMS =====
    print("\n\n### REVIEWS ###")
    try_get(s, f"{BASE}/api/v3/contents/reviews/search?channelNo={CHANNEL_NO}&page=0&size=10", "reviews/search with channelNo")
    try_get(s, f"{BASE}/api/v3/contents/reviews/search?channelNo={CHANNEL_NO}&page=0&size=10&channelProductNo=0", "reviews/search alt params")
    try_get(s, f"{BASE}/api/v3/contents/reviews/sync?channelNo={CHANNEL_NO}", "reviews/sync with channelNo")

    # ===== ORDER PATTERNS (v3) =====
    print("\n\n### ORDERS (v3 patterns) ###")
    try_get(s, f"{BASE}/o/v3/manage/order?channelNo={CHANNEL_NO}", "o/v3/manage/order")
    try_get(s, f"{BASE}/o/v3/n/sale/delivery?channelNo={CHANNEL_NO}", "o/v3/n/sale/delivery")

    # ===== SETTLEMENTS =====
    print("\n\n### SETTLEMENTS ###")
    try_get(s, f"{BASE}/api/settlements?channelNo={CHANNEL_NO}", "settlements with channelNo")
    try_get(s, f"{BASE}/api/settlements?channelNo={CHANNEL_NO}&from={month_ago}&to={today}", "settlements with dates")

    # ===== OTHER USEFUL =====
    print("\n\n### OTHER ###")
    try_get(s, f"{BASE}/api/delivery-bundle-groups?channelNo={CHANNEL_NO}", "delivery-bundle-groups with channelNo")
    try_get(s, f"{BASE}/api/categories?channelNo={CHANNEL_NO}", "categories with channelNo")
    try_get(s, f"{BASE}/api/shared?channelNo={CHANNEL_NO}", "shared with channelNo")

    # ===== TRY /api/context deep dive =====
    print("\n\n### CONTEXT DEEP DIVE ###")
    try_get(s, f"{BASE}/api/context?channelNo={CHANNEL_NO}", "context with channelNo")

    # ===== INQUIRIES =====
    print("\n\n### INQUIRIES ###")
    try_get(s, f"{BASE}/api/seller/talktalk?channelNo={CHANNEL_NO}", "seller/talktalk with channelNo")
    try_get(s, f"{BASE}/api/shared/talktalk?channelNo={CHANNEL_NO}", "shared/talktalk with channelNo")
    try_get(s, f"{BASE}/api/member/nchat/connect?channelNo={CHANNEL_NO}", "member/nchat/connect with channelNo")

    # ===== v2 data-statistics =====
    print("\n\n### DATA STATISTICS V2 ###")
    try_get(s, f"{BASE}/api/v2/data-statistics?channelNo={CHANNEL_NO}", "v2/data-statistics with channelNo")
    try_get(s, f"{BASE}/api/v2/data-statistics?channelNo={CHANNEL_NO}&startDate={month_ago}&endDate={today}", "v2/data-statistics with dates")
    try_get(s, f"{BASE}/api/v2/data-statistics/search-inflow/channel-products?channelNo={CHANNEL_NO}", "v2/data-statistics search-inflow")

    # ===== SELLER GRADE =====
    print("\n\n### SELLER GRADE ###")
    try_get(s, f"{BASE}/api/seller/grade/raw-data?channelNo={CHANNEL_NO}", "seller/grade/raw-data with channelNo")
    try_get(s, f"{BASE}/api/sellers/growth-mileage?channelNo={CHANNEL_NO}", "sellers/growth-mileage")

    # ===== CLAIM / RETURN (v3) =====
    print("\n\n### CLAIMS (v3) ###")
    try_get(s, f"{BASE}/o/v3/claim/returnCare/management?channelNo={CHANNEL_NO}", "v3/claim/returnCare/management")

    # ===== SERVICE OPEN CONTROL =====
    print("\n\n### SERVICE CONTROL ###")
    try_get(s, f"{BASE}/api/service-open-control/?channelNo={CHANNEL_NO}", "service-open-control with channelNo")

    # ===== ENUMS (useful for understanding data shapes) =====
    print("\n\n### ENUMS ###")
    try_get(s, f"{BASE}/api/v2/benefit/enums?enumNames=CouponStatus,ConditionType&channelNo={CHANNEL_NO}", "v2/benefit/enums with enumNames")
    try_get(s, f"{BASE}/api/v2/product-enums/codes?channelNo={CHANNEL_NO}", "v2/product-enums/codes with channelNo")
    try_get(s, f"{BASE}/api/v3/contents-enums/codes?channelNo={CHANNEL_NO}", "v3/contents-enums/codes with channelNo")
    try_get(s, f"{BASE}/api/v1/sellers/shared/codes?channelNo={CHANNEL_NO}", "v1/sellers/shared/codes with channelNo")
    try_get(s, f"{BASE}/api/v1/benefit/enums/codes?channelNo={CHANNEL_NO}", "v1/benefit/enums/codes with channelNo")
    try_get(s, f"{BASE}/api/v2/settlements/enums?channelNo={CHANNEL_NO}", "v2/settlements/enums with channelNo")

    # ===== CREDIT/PENALTY =====
    print("\n\n### CREDIT / PENALTY ###")
    try_get(s, f"{BASE}/api/credit/history?channelNo={CHANNEL_NO}", "credit/history with channelNo")
    try_get(s, f"{BASE}/api/penalty?channelNo={CHANNEL_NO}", "penalty with channelNo")

    # ===== LOGISTICS =====
    print("\n\n### LOGISTICS ###")
    try_get(s, f"{BASE}/api/logistics?channelNo={CHANNEL_NO}", "logistics with channelNo")
    try_get(s, f"{BASE}/api/product/logistics/companies?channelNo={CHANNEL_NO}", "product/logistics/companies with channelNo")

    print("\n\n" + "="*100)
    print("TESTING COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()
