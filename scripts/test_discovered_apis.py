#!/usr/bin/env python3
"""
Test discovered Naver Smart Store seller center API endpoints.
Read-only GET requests only.
Focus on endpoints relevant to: products, orders, stats, settlements, reviews, inquiries, seller info.
"""

import json
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

def try_get(s, url, label=None, show_body=True, max_body=1500):
    label = label or url
    try:
        r = s.get(url, timeout=15, allow_redirects=False)
        status = r.status_code
        ct = r.headers.get("Content-Type", "")
        body = r.text[:max_body] if r.text else "(empty)"
        is_json = "json" in ct.lower()

        indicator = "OK" if status == 200 else ("REDIRECT" if 300 <= status < 400 else f"HTTP {status}")

        print(f"\n{'='*100}")
        print(f"[{indicator}] {label}")
        print(f"  URL: {url}")
        print(f"  Status: {status} | Content-Type: {ct}")
        if 300 <= status < 400:
            print(f"  Location: {r.headers.get('Location', 'N/A')}")
        if show_body:
            if is_json:
                try:
                    parsed = json.loads(r.text)
                    print(f"  JSON Response:")
                    print(f"  {json.dumps(parsed, indent=2, ensure_ascii=False)[:max_body]}")
                except:
                    print(f"  Body: {body}")
            else:
                # Show first bit of non-JSON
                print(f"  Body: {body[:500]}")
        return status, ct, r.text, is_json
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None, None, False

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    print("="*100)
    print("TESTING KEY DISCOVERED API ENDPOINTS")
    print("="*100)

    # ===== 1. CONTEXT / LOGIN / SESSION =====
    print("\n\n" + "#"*100)
    print("# 1. CONTEXT / AUTH / SESSION")
    print("#"*100)

    try_get(s, f"{BASE}/api/context", "api/context - App bootstrap context")
    try_get(s, f"{BASE}/api/login/check", "api/login/check - Check login state")
    try_get(s, f"{BASE}/api/login/channels", "api/login/channels - Available channels")
    try_get(s, f"{BASE}/api/login/roles", "api/login/roles - User roles")
    try_get(s, f"{BASE}/api/login/init", "api/login/init - Login init data")

    # ===== 2. SELLER INFO =====
    print("\n\n" + "#"*100)
    print("# 2. SELLER INFO")
    print("#"*100)

    try_get(s, f"{BASE}/api/seller/info", "api/seller/info - Seller info")
    try_get(s, f"{BASE}/api/sellers", "api/sellers - Sellers")
    try_get(s, f"{BASE}/api/v1/sellers", "api/v1/sellers - Sellers v1")
    try_get(s, f"{BASE}/api/seller-configs", "api/seller-configs - Seller configuration")
    try_get(s, f"{BASE}/api/seller/grade/raw-data", "api/seller/grade/raw-data - Seller grade")
    try_get(s, f"{BASE}/api/channels", "api/channels - Channels")
    try_get(s, f"{BASE}/api/myconfigs", "api/myconfigs - My configs")

    # ===== 3. PRODUCTS =====
    print("\n\n" + "#"*100)
    print("# 3. PRODUCTS")
    print("#"*100)

    try_get(s, f"{BASE}/api/products", "api/products - Products (no params)")
    try_get(s, f"{BASE}/api/products/list", "api/products/list - Product list")
    try_get(s, f"{BASE}/api/products/list/search", "api/products/list/search - Product search")
    try_get(s, f"{BASE}/api/channel-products/list", "api/channel-products/list - Channel products")
    try_get(s, f"{BASE}/api/channel-products/list/search", "api/channel-products/list/search - Channel product search")
    try_get(s, f"{BASE}/api/categories", "api/categories - Categories")

    # ===== 4. ORDERS =====
    print("\n\n" + "#"*100)
    print("# 4. ORDERS")
    print("#"*100)

    try_get(s, f"{BASE}/api/sale-summaries", "api/sale-summaries - Sale summaries")
    try_get(s, f"{BASE}/api/reports", "api/reports - Reports")

    # ===== 5. DASHBOARD =====
    print("\n\n" + "#"*100)
    print("# 5. DASHBOARD")
    print("#"*100)

    try_get(s, f"{BASE}/api/dashboards", "api/dashboards - Dashboards")
    try_get(s, f"{BASE}/api/dashboards/modals", "api/dashboards/modals - Dashboard modals")

    # ===== 6. STATS =====
    print("\n\n" + "#"*100)
    print("# 6. STATISTICS")
    print("#"*100)

    try_get(s, f"{BASE}/api/stats", "api/stats - Stats")
    try_get(s, f"{BASE}/api/sales-day", "api/sales-day - Daily sales")
    try_get(s, f"{BASE}/api/sales-day/with-from-to", "api/sales-day/with-from-to - Sales range")
    try_get(s, f"{BASE}/api/v2/data-statistics", "api/v2/data-statistics - Data statistics v2")

    # ===== 7. SETTLEMENTS =====
    print("\n\n" + "#"*100)
    print("# 7. SETTLEMENTS")
    print("#"*100)

    try_get(s, f"{BASE}/api/settlements", "api/settlements - Settlements")
    try_get(s, f"{BASE}/api/v2/settlements/enums", "api/v2/settlements/enums - Settlement enums")

    # ===== 8. REVIEWS =====
    print("\n\n" + "#"*100)
    print("# 8. REVIEWS")
    print("#"*100)

    try_get(s, f"{BASE}/api/v3/contents/reviews/search", "api/v3/contents/reviews/search - Review search")
    try_get(s, f"{BASE}/api/v3/contents/reviews/dash-board/review-count", "api/v3/contents/reviews/dash-board/review-count - Review count")
    try_get(s, f"{BASE}/api/v3/contents/reviews/dash-board/low-score", "api/v3/contents/reviews/dash-board/low-score - Low score reviews")

    # ===== 9. ORDER MANAGEMENT (iframe/v3 patterns) =====
    print("\n\n" + "#"*100)
    print("# 9. ORDER MANAGEMENT (v3 iframe patterns)")
    print("#"*100)

    try_get(s, f"{BASE}/o/v3/order/summary", "o/v3/order/summary - Order summary")
    try_get(s, f"{BASE}/o/v3/iframe/manage/order", "o/v3/iframe/manage/order - Order management")
    try_get(s, f"{BASE}/o/v3/iframe/n/sale/delivery", "o/v3/iframe/n/sale/delivery - Delivery")
    try_get(s, f"{BASE}/o/v3/iframe/sale/unpayment", "o/v3/iframe/sale/unpayment - Unpayment")

    # ===== 10. OTHER USEFUL =====
    print("\n\n" + "#"*100)
    print("# 10. OTHER USEFUL ENDPOINTS")
    print("#"*100)

    try_get(s, f"{BASE}/api/seller/notification", "api/seller/notification - Notifications")
    try_get(s, f"{BASE}/api/service-open-control", "api/service-open-control - Service controls")
    try_get(s, f"{BASE}/api/v1/sellers/shared/codes", "api/v1/sellers/shared/codes - Shared codes")
    try_get(s, f"{BASE}/api/v2/product-enums/codes", "api/v2/product-enums/codes - Product enum codes")
    try_get(s, f"{BASE}/api/v2/purchases/enums", "api/v2/purchases/enums - Purchase enums")
    try_get(s, f"{BASE}/api/v3/contents-enums/codes", "api/v3/contents-enums/codes - Content enum codes")
    try_get(s, f"{BASE}/api/product/delivery/companies", "api/product/delivery/companies - Delivery companies")
    try_get(s, f"{BASE}/api/delivery-bundle-groups", "api/delivery-bundle-groups - Delivery bundle groups")

    # ===== 11. INQUIRIES =====
    print("\n\n" + "#"*100)
    print("# 11. INQUIRIES / TALK")
    print("#"*100)

    try_get(s, f"{BASE}/api/seller/talktalk", "api/seller/talktalk - TalkTalk config")
    try_get(s, f"{BASE}/api/shared/talktalk", "api/shared/talktalk - Shared TalkTalk")

    # ===== 12. BENEFIT/COUPON =====
    print("\n\n" + "#"*100)
    print("# 12. BENEFIT / COUPON")
    print("#"*100)

    try_get(s, f"{BASE}/api/v1/benefit", "api/v1/benefit - Benefit v1")
    try_get(s, f"{BASE}/api/v2/benefit/enums", "api/v2/benefit/enums - Benefit enums v2")

    print("\n\n" + "="*100)
    print("TESTING COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()
