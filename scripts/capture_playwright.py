#!/usr/bin/env python3
"""Capture API responses using Playwright browser context (correct cookie handling)."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright

PW_STATE_PATH = "/Users/junghoon/Library/Caches/storectl/auth/playwright-storage-state.json"
BASE = "https://sell.smartstore.naver.com"
OUT_DIR = Path("/Users/junghoon/workspace/projects/oss-smartstore-cli/fixtures/responses")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def save(name, data):
    (OUT_DIR / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"  → {name}.json saved")

def api_get(context, path, params=None, label=""):
    url = BASE + path
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url += ("?" if "?" not in url else "&") + qs
    try:
        r = context.request.get(url, headers={
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://sell.smartstore.naver.com/",
        })
        icon = "✓" if r.status == 200 else "✗"
        print(f"{icon} [{r.status}] {label} | GET {path} ({len(r.body())}B)")
        if r.status == 200:
            try:
                return r.json()
            except:
                return None
        else:
            print(f"  {r.text()[:200]}")
        return None
    except Exception as e:
        print(f"✗ [ERR] {label}: {e}")
        return None

def api_post(context, path, body=None, params=None, label=""):
    url = BASE + path
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url += "?" + qs
    try:
        r = context.request.post(url, data=json.dumps(body or {}), headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Referer": "https://sell.smartstore.naver.com/",
        })
        icon = "✓" if r.status == 200 else "✗"
        print(f"{icon} [{r.status}] {label} | POST {path} ({len(r.body())}B)")
        if r.status == 200:
            try:
                return r.json()
            except:
                return None
        else:
            print(f"  {r.text()[:200]}")
        return None
    except Exception as e:
        print(f"✗ [ERR] {label}: {e}")
        return None

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(storage_state=PW_STATE_PATH)

        # Step 1: Login channels
        print("=" * 80)
        print("STEP 1: Login channels")
        data = api_get(context, "/api/login/channels", label="login/channels")
        if data and isinstance(data, list) and data:
            ch = data[0]
            channel_no = ch["channelNo"]
            role_no = ch["roleNo"]
            print(f"  channelNo={channel_no}, roleNo={role_no}, name={ch.get('channelName')}")
            save("login-channels", data)
        else:
            channel_no = 1100114368
            role_no = 200206319
            print(f"  Using cached values: channelNo={channel_no}, roleNo={role_no}")

        # Step 2: Change channel
        print("\n" + "=" * 80)
        print("STEP 2: Change channel")
        r = context.request.post(
            f"{BASE}/api/login/change-channel?roleNo={role_no}&channelNo={channel_no}&url=%2F",
            headers={"Referer": "https://sell.smartstore.naver.com/"},
        )
        print(f"  Status: {r.status}")

        # Step 3: Init
        print("\nSTEP 3: Init")
        data = api_get(context, "/api/login/init",
                       {"stateName": "home.dashboard", "needLoginInfoForAngular": "true"},
                       "login/init")
        if data:
            save("login-init", data)

        # Step 4: Test all endpoints
        print("\n" + "=" * 80)
        print("STEP 4: Test endpoints")
        print("=" * 80)

        today = datetime.now().strftime("%Y%m%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        today_iso = datetime.now().strftime("%Y-%m-%d")

        ok = 0
        tests = [
            # Dashboard
            ("GET", "/api/dashboards/pay/sale-stats", None, None, "dashboard-sale-stats"),
            ("GET", "/api/dashboards/pay/order-delivery", None, None, "dashboard-order-delivery"),
            ("GET", "/api/dashboards/channel/products", None, None, "dashboard-products"),
            ("GET", "/api/dashboards/pay/settlement", None, None, "dashboard-settlement"),
            ("GET", "/api/dashboards/pay/claim", None, None, "dashboard-claim"),
            ("GET", "/api/dashboards/seller-grade", None, None, "dashboard-seller-grade"),
            ("GET", "/api/dashboards/pay/purchase-completion", None, None, "dashboard-purchase"),
            ("GET", "/api/dashboards/pay/sales-delay", None, None, "dashboard-delay"),
            ("GET", "/api/dashboards/channel/sale-performance", None, None, "dashboard-performance"),
            ("GET", "/api/dashboards/best-keyword", None, None, "dashboard-keyword"),
            # Sales
            ("GET", "/api/sales-day/with-from-to", {"fromDateString": week_ago, "toDateString": today}, None, "sales-day"),
            # Seller
            ("GET", "/api/seller/info", None, None, "seller-info"),
            ("GET", "/api/v1/sellers", None, None, "sellers-v1"),
            ("GET", "/api/seller/notification", None, None, "notification"),
            # Channel
            ("GET", "/api/channels", {"_action": "selectedChannel"}, None, "channel-selected"),
            ("GET", "/api/myconfigs", {"_action": "getChannels"}, None, "myconfigs"),
            # Reviews
            ("GET", "/api/v3/contents/reviews/dash-board/review-count", None, None, "reviews-count"),
            ("GET", "/api/v3/contents/reviews/dash-board/low-score", None, None, "reviews-low-score"),
            # Products
            ("POST", "/api/channel-products/list/search", None, {"page": 1, "pageSize": 10}, "products-search"),
            ("POST", "/api/products/list/search", None, {"page": 1, "pageSize": 10}, "products-list"),
            # Others
            ("GET", "/api/credit/history", {"_action": "init", "startDate": month_ago, "endDate": today_iso}, None, "credit-history"),
            ("GET", "/api/product/delivery/companies", None, None, "delivery-companies"),
            ("GET", "/api/settlements", {"_action": "queryPage"}, None, "settlements"),
            ("GET", "/api/sale-summaries", {"_action": "queryPage"}, None, "sale-summaries"),
            ("GET", "/api/v2/product-enums/codes", {"enumNames": "ProductStatusType"}, None, "product-enums"),
            ("GET", "/api/categories", None, None, "categories"),
            ("POST", "/api/v3/contents/reviews/search", None, {"page": 1, "pageSize": 10}, "reviews-search"),
            ("GET", "/api/context", None, None, "context"),
        ]

        for method, path, params, body, name in tests:
            if method == "POST":
                data = api_post(context, path, body, params, name)
            else:
                data = api_get(context, path, params, name)
            if data:
                save(name, data)
                ok += 1

        browser.close()

    print(f"\n{'='*80}")
    print(f"RESULT: {ok}/{len(tests)} endpoints OK")

if __name__ == "__main__":
    main()
