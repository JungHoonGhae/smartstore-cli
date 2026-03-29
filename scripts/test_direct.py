#!/usr/bin/env python3
"""Test API endpoints directly - session may already be channel-activated."""

import json
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")
import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"

def load_session():
    with open(SESSION_PATH) as f:
        return json.load(f)

def make_session(sess_data):
    s = requests.Session()
    # Set all cookies for the seller center domain
    for name, value in sess_data.get("cookies", {}).items():
        s.cookies.set(name, value, domain=".smartstore.naver.com", path="/")
    # Also set NID cookies for .naver.com domain
    for name, value in sess_data.get("cookies", {}).items():
        if any(name.startswith(p) for p in ("NID", "NNB", "nid", "SRT", "NAC")) or name == "BUC":
            s.cookies.set(name, value, domain=".naver.com", path="/")
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://sell.smartstore.naver.com/",
        "Origin": "https://sell.smartstore.naver.com",
    })
    return s

def pj(r, max_body=3000):
    try:
        d = r.json()
        txt = json.dumps(d, indent=2, ensure_ascii=False)
        return txt[:max_body] + ("\n  ... (truncated)" if len(txt) > max_body else "")
    except:
        return r.text[:500]

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    # Try login/init first
    print("=== Try login/init ===")
    r = s.get(f"{BASE}/api/login/init",
              params={"stateName": "home.dashboard", "needLoginInfoForAngular": "true"},
              timeout=15)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        d = r.json()
        print(f"Keys: {list(d.keys())[:15]}")
        for k in ("channelNo", "accountNo", "channelName", "loginId", "roleGroupType"):
            if k in d:
                print(f"  {k}: {d[k]}")
    else:
        print(pj(r, 500))

    # Test main data endpoints
    today = datetime.now().strftime("%Y%m%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

    tests = [
        ("GET", "/api/dashboards/pay/sale-stats", None, None, "대시보드 매출"),
        ("GET", "/api/dashboards/pay/order-delivery", None, None, "대시보드 주문배송"),
        ("GET", "/api/dashboards/channel/products", None, None, "대시보드 상품"),
        ("GET", "/api/dashboards/pay/settlement", None, None, "대시보드 정산"),
        ("GET", "/api/dashboards/pay/claim", None, None, "대시보드 클레임"),
        ("GET", "/api/dashboards/seller-grade", None, None, "판매자 등급"),
        ("GET", "/api/dashboards/pay/purchase-completion", None, None, "구매확정"),
        ("GET", "/api/dashboards/pay/sales-delay", None, None, "배송지연"),
        ("GET", "/api/dashboards/channel/sale-performance", None, None, "채널 판매성과"),
        ("GET", "/api/dashboards/best-keyword", None, None, "베스트키워드"),
        ("GET", "/api/dashboards/modals", None, None, "대시보드 모달"),
        ("GET", "/api/v3/contents/reviews/dash-board/review-count", None, None, "리뷰수"),
        ("GET", "/api/v3/contents/reviews/dash-board/low-score", None, None, "저점수 리뷰"),
        ("GET", f"/api/sales-day/with-from-to", {"fromDateString": week_ago, "toDateString": today}, None, "일별매출"),
        ("GET", "/api/seller/info", None, None, "판매자 정보"),
        ("GET", "/api/seller/notification", None, None, "알림"),
        ("GET", "/api/credit/history", {"_action": "init", "startDate": "2026-03-01", "endDate": "2026-03-26"}, None, "신용이력"),
        ("GET", "/api/channels", {"_action": "selectedChannel"}, None, "선택채널"),
        ("GET", "/api/myconfigs", {"_action": "getChannels"}, None, "채널설정"),
        ("POST", "/api/channel-products/list/search", None, {"page": 1, "pageSize": 10, "productStatusTypes": ["SALE"]}, "상품검색"),
        ("POST", "/api/products/list/search", None, {"page": 1, "pageSize": 10}, "상품목록검색"),
        ("GET", "/api/product/delivery/companies", None, None, "택배사"),
    ]

    print(f"\n{'='*80}")
    print(f"Testing {len(tests)} endpoints")
    print(f"{'='*80}")

    for method, path, params, body, label in tests:
        url = BASE + path
        try:
            if method == "POST":
                r = s.post(url, json=body or {}, params=params, timeout=15)
            else:
                r = s.get(url, params=params, timeout=15)
            icon = "✓" if r.status_code == 200 else "✗"
            print(f"\n{icon} [{r.status_code}] {label} | {method} {path}")
            if r.status_code == 200:
                print(pj(r, 2000))
        except Exception as e:
            print(f"\n✗ [ERR] {label}: {e}")

if __name__ == "__main__":
    main()
