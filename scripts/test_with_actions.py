#!/usr/bin/env python3
"""
Test APIs with the correct _action parameters and login/init flow.
From app.js analysis:
- login/init uses GET with {stateName, needLoginInfoForAngular}
- Most list endpoints use _action param (e.g., _action=queryPage)
- categories uses _action=queryPage
- delivery-bundle-groups uses _action=queryPage or _action=base
- sale-summaries uses _action=queryPage
- settlements uses _action=queryPage
- myconfigs uses _action=getChannels
- channels uses _action=selectedChannel
- shared/talktalk uses _action=isTalkExposure
- credit/history uses _action=init or GET with dates
- penalty uses _action=getProhibitProductRegistAccounts
- seller/info has direct GET with ssnShow param
- dashboards has sub-paths like /pay/sale-stats, /pay/order-delivery, etc.
"""

import json
import sys
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"
CHANNEL_NO = 1100114368
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
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://sell.smartstore.naver.com/",
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
                    print(f"  ... (truncated, {len(pretty)} total)")
            except:
                print(f"  Raw: {r.text[:max_body]}")
        else:
            print(f"  Body: {r.text[:500]}")
        return status, r.text
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    today = datetime.now().strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # Step 0: POST to change-channel first
    print("="*100)
    print("STEP 0: POST /api/login/change-channel")
    print("="*100)
    r = s.post(f"{BASE}/api/login/change-channel?roleNo={ROLE_NO}&channelNo={CHANNEL_NO}&url=%2F",
               timeout=15, allow_redirects=False)
    print(f"  change-channel: {r.status_code}")

    # Step 1: login/init
    print("\n" + "="*100)
    print("STEP 1: GET /api/login/init")
    print("="*100)
    try_get(s, f"{BASE}/api/login/init?stateName=main.home.dashboard&needLoginInfoForAngular=true", "login/init")

    # Step 2: Test endpoints with _action params
    print("\n" + "="*100)
    print("STEP 2: Test endpoints with _action parameters")
    print("="*100)

    # Categories with _action
    try_get(s, f"{BASE}/api/categories?_action=queryPage", "categories _action=queryPage")

    # Delivery bundle groups
    try_get(s, f"{BASE}/api/delivery-bundle-groups?_action=queryPage", "delivery-bundle-groups _action=queryPage")
    try_get(s, f"{BASE}/api/delivery-bundle-groups?_action=base", "delivery-bundle-groups _action=base")

    # Sale summaries
    try_get(s, f"{BASE}/api/sale-summaries?_action=queryPage", "sale-summaries _action=queryPage")

    # Settlements
    try_get(s, f"{BASE}/api/settlements?_action=queryPage", "settlements _action=queryPage")

    # MyConfigs
    try_get(s, f"{BASE}/api/myconfigs?_action=getChannels", "myconfigs _action=getChannels")
    try_get(s, f"{BASE}/api/myconfigs?_action=getJoinApplyChannels", "myconfigs _action=getJoinApplyChannels")

    # Channels
    try_get(s, f"{BASE}/api/channels?_action=selectedChannel", "channels _action=selectedChannel")
    try_get(s, f"{BASE}/api/channels?_action=managedChannelList", "channels _action=managedChannelList")
    try_get(s, f"{BASE}/api/channels?_action=groupManagerChannelList", "channels _action=groupManagerChannelList")

    # Shared/TalkTalk
    try_get(s, f"{BASE}/api/shared/talktalk?_action=isTalkExposure&channelNo={CHANNEL_NO}", "shared/talktalk _action=isTalkExposure")

    # Credit/History
    try_get(s, f"{BASE}/api/credit/history?_action=init", "credit/history _action=init")

    # Penalty
    try_get(s, f"{BASE}/api/penalty?_action=getProhibitProductRegistAccounts", "penalty _action=getProhibitProductRegistAccounts")

    # Dashboard sub-endpoints
    print("\n" + "="*100)
    print("STEP 3: Dashboard sub-endpoints")
    print("="*100)

    dashboard_endpoints = [
        "/api/dashboards/pay/sale-stats",
        "/api/dashboards/pay/order-delivery",
        "/api/dashboards/pay/claim",
        "/api/dashboards/pay/purchase-completion",
        "/api/dashboards/pay/sales-delay",
        "/api/dashboards/pay/settlement",
        "/api/dashboards/channel/products",
        "/api/dashboards/account/penalties",
        "/api/dashboards/seller-grade",
        "/api/dashboards/best-price-products",
        "/api/dashboards/banners",
        "/api/dashboards/talktalk-reception-status",
        "/api/dashboards/naver-shopping-search-trend",
        "/api/dashboards/channel/sale-performance",
        "/api/dashboards/best-keyword",
    ]
    for ep in dashboard_endpoints:
        try_get(s, f"{BASE}{ep}", ep)

    # Seller info
    print("\n" + "="*100)
    print("STEP 4: Seller info variants")
    print("="*100)

    try_get(s, f"{BASE}/api/seller/info", "seller/info (no params)")
    try_get(s, f"{BASE}/api/seller/info?ssnShow=true", "seller/info?ssnShow=true")
    try_get(s, f"{BASE}/api/sellers/account", "sellers/account")
    try_get(s, f"{BASE}/api/sellers/account?mask=true&maskApplyTypes=ALL", "sellers/account?mask=true")
    try_get(s, f"{BASE}/api/sellers/bank-account", "sellers/bank-account")

    # Sellers with menu toggle
    try_get(s, f"{BASE}/api/v1/sellers/menus/toggles/ALL", "v1/sellers/menus/toggles/ALL")

    # Enum endpoints with proper params
    print("\n" + "="*100)
    print("STEP 5: Enum endpoints")
    print("="*100)

    try_get(s, f"{BASE}/api/v1/sellers/shared/codes?enumNames=AccountStatusType,ChannelType", "v1/sellers/shared/codes with enumNames")
    try_get(s, f"{BASE}/api/v2/product-enums/codes?enumNames=ProductStatusType", "v2/product-enums/codes with enumNames")
    try_get(s, f"{BASE}/api/v3/contents-enums/codes?enumNames=ReviewContentType", "v3/contents-enums/codes with enumNames")

    # Channel-specific endpoints
    print("\n" + "="*100)
    print("STEP 6: Channel-specific endpoints")
    print("="*100)

    try_get(s, f"{BASE}/api/channels/{CHANNEL_NO}", f"channels/{CHANNEL_NO}")
    try_get(s, f"{BASE}/api/channels/{CHANNEL_NO}?mask=true", f"channels/{CHANNEL_NO}?mask=true")

    # Sales day with correct params
    try_get(s, f"{BASE}/api/sales-day/with-from-to?fromDateString={month_ago}&toDateString={today}",
            "sales-day/with-from-to (correct params)")

    # Dynamic pricing dashboard
    try_get(s, f"{BASE}/api/v2/products/dynamic-pricing/summary-for-dashboard",
            "v2/products/dynamic-pricing/summary-for-dashboard")

    print("\n\n" + "="*100)
    print("TESTING COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()
