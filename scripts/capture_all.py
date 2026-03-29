#!/usr/bin/env python3
"""Capture all API responses in one shot: channels → change-channel → init → endpoints."""

import json
import sys
import warnings
from datetime import datetime, timedelta
from pathlib import Path

warnings.filterwarnings("ignore")
import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"
OUT_DIR = Path("/Users/junghoon/workspace/projects/oss-smartstore-cli/fixtures/responses")

def load_session():
    with open(SESSION_PATH) as f:
        return json.load(f)

def make_session(sess_data):
    s = requests.Session()
    for name, value in sess_data.get("cookies", {}).items():
        s.cookies.set(name, value, domain="sell.smartstore.naver.com", path="/")
    for name, value in sess_data.get("cookies", {}).items():
        if any(name.startswith(p) for p in ("NID", "NNB", "nid", "SRT", "NAC")) or name == "BUC":
            s.cookies.set(name, value, domain=".naver.com", path="/")
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://sell.smartstore.naver.com/",
        "Origin": "https://sell.smartstore.naver.com",
    })
    return s

def save_response(name, data):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"  → Saved: {path.name}")

def main():
    sess_data = load_session()
    s = make_session(sess_data)
    results = {}

    # === Step 1: Get channels ===
    print("STEP 1: GET /api/login/channels")
    r = s.get(f"{BASE}/api/login/channels", timeout=15)
    print(f"  Status: {r.status_code}")
    if r.status_code != 200:
        print(f"  FAILED: {r.text[:300]}")
        return
    channels = r.json()
    ch = channels[0]
    channel_no = ch["channelNo"]
    role_no = ch["roleNo"]
    print(f"  channelNo={channel_no}, roleNo={role_no}, name={ch.get('channelName')}")
    save_response("login-channels", channels)

    # === Step 2: POST change-channel ===
    print("\nSTEP 2: POST /api/login/change-channel")
    r = s.post(f"{BASE}/api/login/change-channel",
               params={"roleNo": role_no, "channelNo": channel_no, "url": "/"},
               timeout=15, allow_redirects=False)
    print(f"  Status: {r.status_code}, x-ses-valid: {r.headers.get('x-ses-valid', 'N/A')}")

    # === Step 3: GET login/init ===
    print("\nSTEP 3: GET /api/login/init")
    r = s.get(f"{BASE}/api/login/init",
              params={"stateName": "home.dashboard", "needLoginInfoForAngular": "true"},
              timeout=15)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        body = r.text.strip()
        if body:
            init_data = r.json()
            for k in ("channelNo", "accountNo", "channelName", "loginId", "roleGroupType"):
                if k in init_data:
                    print(f"  {k}: {init_data[k]}")
            save_response("login-init", init_data)
        else:
            print("  (empty body - session initialized)")

    # === Step 4: Test all endpoints ===
    print(f"\n{'='*80}")
    print("STEP 4: Test endpoints")
    print(f"{'='*80}")

    today = datetime.now().strftime("%Y%m%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
    month_ago_iso = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    today_iso = datetime.now().strftime("%Y-%m-%d")

    tests = [
        # Dashboard endpoints (GET)
        ("GET", "/api/dashboards/pay/sale-stats", None, None, "dashboard-sale-stats"),
        ("GET", "/api/dashboards/pay/order-delivery", None, None, "dashboard-order-delivery"),
        ("GET", "/api/dashboards/channel/products", None, None, "dashboard-products"),
        ("GET", "/api/dashboards/pay/settlement", None, None, "dashboard-settlement"),
        ("GET", "/api/dashboards/pay/claim", None, None, "dashboard-claim"),
        ("GET", "/api/dashboards/seller-grade", None, None, "dashboard-seller-grade"),
        ("GET", "/api/dashboards/pay/purchase-completion", None, None, "dashboard-purchase-completion"),
        ("GET", "/api/dashboards/pay/sales-delay", None, None, "dashboard-sales-delay"),
        ("GET", "/api/dashboards/channel/sale-performance", None, None, "dashboard-sale-performance"),
        ("GET", "/api/dashboards/best-keyword", None, None, "dashboard-best-keyword"),
        ("GET", "/api/dashboards/modals", None, None, "dashboard-modals"),
        ("GET", "/api/dashboards/banners", None, None, "dashboard-banners"),

        # Sales/Stats
        ("GET", "/api/sales-day/with-from-to", {"fromDateString": week_ago, "toDateString": today}, None, "sales-day"),

        # Seller info
        ("GET", "/api/seller/info", None, None, "seller-info"),
        ("GET", "/api/v1/sellers", None, None, "sellers-v1"),
        ("GET", "/api/seller/notification", None, None, "seller-notification"),

        # Channel & config
        ("GET", "/api/channels", {"_action": "selectedChannel"}, None, "channel-selected"),
        ("GET", "/api/myconfigs", {"_action": "getChannels"}, None, "myconfigs-channels"),

        # Reviews
        ("GET", "/api/v3/contents/reviews/dash-board/review-count", None, None, "reviews-count"),
        ("GET", "/api/v3/contents/reviews/dash-board/low-score", None, None, "reviews-low-score"),

        # Products (POST search)
        ("POST", "/api/channel-products/list/search", None,
         {"page": 1, "pageSize": 10, "productStatusTypes": ["SALE"]}, "products-search"),
        ("POST", "/api/products/list/search", None,
         {"page": 1, "pageSize": 10}, "products-list-search"),

        # Credit
        ("GET", "/api/credit/history", {"_action": "init", "startDate": month_ago_iso, "endDate": today_iso}, None, "credit-history"),

        # Delivery
        ("GET", "/api/product/delivery/companies", None, None, "delivery-companies"),
        ("GET", "/api/delivery-bundle-groups", {"_action": "queryPage"}, None, "delivery-groups"),

        # Settlements
        ("GET", "/api/settlements", {"_action": "queryPage"}, None, "settlements"),
        ("GET", "/api/sale-summaries", {"_action": "queryPage"}, None, "sale-summaries"),

        # Context
        ("GET", "/api/context", None, None, "context"),

        # Enums
        ("GET", "/api/v2/product-enums/codes", {"enumNames": "ProductStatusType,ChannelProductDisplayStatusType"}, None, "product-enums"),
    ]

    ok_count = 0
    fail_count = 0
    for method, path, params, body, filename in tests:
        url = BASE + path
        try:
            if method == "POST":
                r = s.post(url, json=body or {}, params=params, timeout=15)
            else:
                r = s.get(url, params=params, timeout=15)

            icon = "✓" if r.status_code == 200 else "✗"
            size = len(r.text)
            print(f"\n{icon} [{r.status_code}] {filename} | {method} {path} ({size}B)")

            if r.status_code == 200:
                ok_count += 1
                try:
                    data = r.json()
                    save_response(filename, data)
                    # Print summary
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())[:10]}")
                    elif isinstance(data, list):
                        print(f"  Array length: {len(data)}")
                except:
                    print(f"  (non-JSON: {r.text[:200]})")
            else:
                fail_count += 1
                print(f"  {r.text[:200]}")
        except Exception as e:
            fail_count += 1
            print(f"\n✗ [ERR] {filename}: {e}")

    print(f"\n{'='*80}")
    print(f"DONE: {ok_count} OK, {fail_count} FAILED")

if __name__ == "__main__":
    main()
