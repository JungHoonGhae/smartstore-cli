#!/usr/bin/env python3
"""Test API with proper session initialization: change-channel → init → test."""

import json
import sys
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
    for name, value in sess_data.get("cookies", {}).items():
        s.cookies.set(name, value, domain="sell.smartstore.naver.com", path="/")
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
    """Pretty print JSON response."""
    try:
        d = r.json()
        txt = json.dumps(d, indent=2, ensure_ascii=False)
        return txt[:max_body] + ("\n  ... (truncated)" if len(txt) > max_body else "")
    except:
        return r.text[:500]

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    # Step 1: Get channels (before change-channel)
    print("=" * 80)
    print("STEP 1: GET /api/login/channels")
    r = s.get(f"{BASE}/api/login/channels", timeout=15)
    print(f"  Status: {r.status_code}")
    channels = r.json() if r.status_code == 200 else []
    if r.status_code == 200:
        print(pj(r, 1000))
        if isinstance(channels, list) and channels:
            ch = channels[0]
            channel_no = ch.get("channelNo")
            role_no = ch.get("roleNo")
            print(f"\n  Using channelNo={channel_no}, roleNo={role_no}")
    else:
        print(f"  Error: {r.text[:300]}")
        return

    # Step 2: POST change-channel
    print("\n" + "=" * 80)
    print("STEP 2: POST /api/login/change-channel")
    r = s.post(
        f"{BASE}/api/login/change-channel",
        params={"roleNo": role_no, "channelNo": channel_no, "url": "/"},
        timeout=15,
        allow_redirects=False,
    )
    print(f"  Status: {r.status_code}")
    print(f"  x-ses-valid: {r.headers.get('x-ses-valid', 'N/A')}")
    # Capture any new cookies from Set-Cookie
    for cookie in r.cookies:
        print(f"  New cookie: {cookie.name}={cookie.value[:30]}...")

    # Step 3: GET /api/login/init
    print("\n" + "=" * 80)
    print("STEP 3: GET /api/login/init")
    r = s.get(
        f"{BASE}/api/login/init",
        params={"stateName": "home.dashboard", "needLoginInfoForAngular": "true"},
        timeout=15,
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        init_data = r.json()
        print(f"  Keys: {list(init_data.keys())[:20]}")
        # Print a subset
        for key in ("channelNo", "accountNo", "roleGroupType", "channelName", "loginId"):
            if key in init_data:
                print(f"  {key}: {init_data[key]}")
    else:
        print(f"  Error: {pj(r, 500)}")

    # Step 4: Test endpoints
    print("\n" + "=" * 80)
    print("STEP 4: Test endpoints after full init")
    print("=" * 80)

    endpoints = [
        ("GET", "/api/seller/info", None, "판매자 정보"),
        ("GET", "/api/v1/sellers", None, "판매자 정보 v1"),
        ("GET", "/api/channels", {"_action": "selectedChannel"}, "선택된 채널"),
        ("GET", "/api/dashboards/pay/sale-stats", None, "매출 통계"),
        ("GET", "/api/dashboards/pay/order-delivery", None, "주문/배송"),
        ("GET", "/api/dashboards/channel/products", None, "상품 현황"),
        ("GET", "/api/dashboards/pay/settlement", None, "정산"),
        ("GET", "/api/dashboards/pay/claim", None, "클레임"),
        ("GET", "/api/dashboards/seller-grade", None, "판매자 등급"),
        ("GET", "/api/dashboards/pay/purchase-completion", None, "구매확정"),
        ("GET", "/api/seller/notification", None, "알림"),
        ("GET", "/api/v3/contents/reviews/dash-board/review-count", None, "리뷰 수"),
        ("GET", "/api/v3/contents/reviews/dash-board/low-score", None, "저점수 리뷰"),
        ("GET", f"/api/sales-day/with-from-to", {
            "fromDateString": (datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
            "toDateString": datetime.now().strftime("%Y%m%d"),
        }, "일별 매출"),
        ("GET", "/api/credit/history", {
            "_action": "init",
            "startDate": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d"),
        }, "신용 이력"),
        ("GET", "/api/myconfigs", {"_action": "getChannels"}, "채널 설정"),
        ("GET", "/api/delivery-bundle-groups", {"_action": "queryPage"}, "배송 그룹"),
        ("POST", "/api/channel-products/list/search", None, "상품 검색 (POST)"),
    ]

    for method, path, params, label in endpoints:
        url = BASE + path
        try:
            if method == "POST":
                r = s.post(url, json={"page": 1, "pageSize": 10}, params=params, timeout=15)
            else:
                r = s.get(url, params=params, timeout=15)

            status_icon = "✓" if r.status_code == 200 else "✗"
            print(f"\n{status_icon} [{r.status_code}] {label} ({path})")
            if r.status_code == 200:
                print(pj(r, 2000))
            else:
                print(f"  {pj(r, 300)}")
        except Exception as e:
            print(f"\n✗ [ERR] {label}: {e}")

    print("\n" + "=" * 80)
    print("DONE")

if __name__ == "__main__":
    main()
