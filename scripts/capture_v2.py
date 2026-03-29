#!/usr/bin/env python3
"""Capture API responses using Playwright storage state with correct cookie domains."""

import json
import warnings
from datetime import datetime, timedelta
from pathlib import Path

warnings.filterwarnings("ignore")
import requests

PW_STATE_PATH = "/Users/junghoon/Library/Caches/storectl/auth/playwright-storage-state.json"
BASE = "https://sell.smartstore.naver.com"
OUT_DIR = Path("/Users/junghoon/workspace/projects/oss-smartstore-cli/fixtures/responses")

def make_session():
    """Build requests.Session with cookies on their original domains."""
    with open(PW_STATE_PATH) as f:
        state = json.load(f)

    s = requests.Session()
    for c in state.get("cookies", []):
        domain = c["domain"]
        # requests needs domain without leading dot for exact match
        s.cookies.set(c["name"], c["value"], domain=domain, path=c.get("path", "/"))

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
    (OUT_DIR / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

def test(s, method, path, params=None, body=None, label=""):
    url = BASE + path
    try:
        if method == "POST":
            r = s.post(url, json=body or {}, params=params, timeout=15)
        else:
            r = s.get(url, params=params, timeout=15)
        icon = "✓" if r.status_code == 200 else "✗"
        print(f"{icon} [{r.status_code}] {label} | {method} {path} ({len(r.text)}B)")
        if r.status_code == 200 and r.text.strip():
            try:
                data = r.json()
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:12]}")
                elif isinstance(data, list):
                    print(f"  Array[{len(data)}]")
                return data
            except:
                print(f"  (non-JSON)")
                return r.text
        elif r.status_code != 200:
            print(f"  {r.text[:200]}")
        return None
    except Exception as e:
        print(f"✗ [ERR] {label}: {e}")
        return None

def main():
    s = make_session()

    # Step 1: Get channels
    print("=" * 80)
    print("STEP 1: Login channels")
    data = test(s, "GET", "/api/login/channels", label="login/channels")
    if not data:
        print("\nFallback: trying context endpoint")
        data = test(s, "GET", "/api/context", label="context")
        if data:
            save_response("context", data)
        # Try with all cookies forced to sell.smartstore.naver.com
        print("\nFallback 2: force all cookies to sell.smartstore.naver.com")
        with open(PW_STATE_PATH) as f:
            state = json.load(f)
        for c in state.get("cookies", []):
            s.cookies.set(c["name"], c["value"], domain="sell.smartstore.naver.com", path="/")
        data = test(s, "GET", "/api/login/channels", label="login/channels (forced domain)")
        if not data:
            print("Still failed. Trying change-channel with known values...")

    if data and isinstance(data, list) and data:
        ch = data[0]
        channel_no = ch["channelNo"]
        role_no = ch["roleNo"]
        print(f"  → channelNo={channel_no}, roleNo={role_no}")
        save_response("login-channels", data)
    else:
        channel_no = 1100114368
        role_no = 200206319
        print(f"  → Using cached: channelNo={channel_no}, roleNo={role_no}")

    # Step 2: change-channel
    print("\n" + "=" * 80)
    print("STEP 2: Change channel")
    r = s.post(f"{BASE}/api/login/change-channel",
               params={"roleNo": role_no, "channelNo": channel_no, "url": "/"},
               timeout=15, allow_redirects=False)
    print(f"  Status: {r.status_code}, x-ses-valid: {r.headers.get('x-ses-valid', 'N/A')}")

    # Step 3: init
    print("\nSTEP 3: Init")
    r = s.get(f"{BASE}/api/login/init",
              params={"stateName": "home.dashboard", "needLoginInfoForAngular": "true"},
              timeout=15)
    print(f"  Status: {r.status_code}, body_len: {len(r.text)}")
    if r.text.strip():
        try:
            init_data = r.json()
            save_response("login-init", init_data)
            for k in ("channelNo", "accountNo", "channelName", "loginId"):
                if k in init_data:
                    print(f"  {k}: {init_data[k]}")
        except:
            pass

    # Step 4: Test all endpoints
    print("\n" + "=" * 80)
    print("STEP 4: Test endpoints")
    print("=" * 80)

    today = datetime.now().strftime("%Y%m%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    today_iso = datetime.now().strftime("%Y-%m-%d")

    endpoints = [
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
        ("GET", "/api/dashboards/modals", None, None, "dashboard-modals"),
        ("GET", "/api/dashboards/banners", None, None, "dashboard-banners"),
        ("GET", "/api/sales-day/with-from-to", {"fromDateString": week_ago, "toDateString": today}, None, "sales-day"),
        ("GET", "/api/seller/info", None, None, "seller-info"),
        ("GET", "/api/v1/sellers", None, None, "sellers-v1"),
        ("GET", "/api/seller/notification", None, None, "seller-notification"),
        ("GET", "/api/channels", {"_action": "selectedChannel"}, None, "channel-selected"),
        ("GET", "/api/myconfigs", {"_action": "getChannels"}, None, "myconfigs"),
        ("GET", "/api/v3/contents/reviews/dash-board/review-count", None, None, "reviews-count"),
        ("GET", "/api/v3/contents/reviews/dash-board/low-score", None, None, "reviews-low-score"),
        ("POST", "/api/channel-products/list/search", None, {"page": 1, "pageSize": 10}, "products-search"),
        ("POST", "/api/products/list/search", None, {"page": 1, "pageSize": 10}, "products-list"),
        ("GET", "/api/credit/history", {"_action": "init", "startDate": month_ago, "endDate": today_iso}, None, "credit-history"),
        ("GET", "/api/product/delivery/companies", None, None, "delivery-companies"),
        ("GET", "/api/delivery-bundle-groups", {"_action": "queryPage"}, None, "delivery-groups"),
        ("GET", "/api/settlements", {"_action": "queryPage"}, None, "settlements"),
        ("GET", "/api/sale-summaries", {"_action": "queryPage"}, None, "sale-summaries"),
        ("GET", "/api/v2/product-enums/codes", {"enumNames": "ProductStatusType,ChannelProductDisplayStatusType"}, None, "product-enums"),
        ("GET", "/api/categories", None, None, "categories"),
        ("POST", "/api/v3/contents/reviews/search", None, {"page": 1, "pageSize": 10}, "reviews-search"),
    ]

    ok = 0
    for method, path, params, body, name in endpoints:
        data = test(s, method, path, params, body, name)
        if data:
            save_response(name, data)
            ok += 1

    print(f"\n{'='*80}")
    print(f"RESULT: {ok}/{len(endpoints)} endpoints returned 200")

if __name__ == "__main__":
    main()
