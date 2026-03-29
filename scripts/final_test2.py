#!/usr/bin/env python3
"""
Final investigation:
- api/login/channels works (200) but api/seller/info doesn't (400)
- The difference might be channel selection / session initialization
- Let's try: 1) change-channel flow, 2) different cookie domains, 3) POST for list endpoints
"""

import json
import re
import sys
import warnings
from datetime import datetime, timedelta
from urllib.parse import quote

warnings.filterwarnings("ignore")

import requests

SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
BASE = "https://sell.smartstore.naver.com"
CHANNEL_NO = 1100114368
ACCOUNT_NO = 1100112229

def load_session():
    with open(SESSION_PATH) as f:
        return json.load(f)

def make_session(sess_data):
    s = requests.Session()
    # Set cookies on all relevant domains
    for name, value in sess_data.get("cookies", {}).items():
        s.cookies.set(name, value, domain="sell.smartstore.naver.com", path="/")
    # Also on .naver.com for NID cookies
    for name, value in sess_data.get("cookies", {}).items():
        if name.startswith("NID") or name.startswith("NNB") or name.startswith("nid") or name.startswith("SRT") or name == "BUC" or name.startswith("NAC"):
            s.cookies.set(name, value, domain=".naver.com", path="/")
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
        print(f"\n[{indicator}] {label}")
        print(f"  Status: {status} | CT: {ct}")
        if is_json:
            try:
                parsed = json.loads(r.text)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                print(f"  JSON ({len(r.text)} bytes): {pretty[:max_body]}")
            except:
                print(f"  Raw: {r.text[:max_body]}")
        else:
            print(f"  Body: {r.text[:500]}")
        # Show response headers that might be interesting
        for h in ['Set-Cookie', 'X-Ses-Valid', 'X-NCP-LOGIN-INFO']:
            if h in r.headers:
                print(f"  Response Header {h}: {r.headers[h][:200]}")
        return status, ct, r.text, r
    except Exception as e:
        print(f"\n[ERROR] {label}: {e}")
        return None, None, None, None

def main():
    sess_data = load_session()
    s = make_session(sess_data)

    today = datetime.now().strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # ===== Step 1: Call login/channels first (which works) and check response cookies =====
    print("="*100)
    print("STEP 1: Call login/channels and inspect response for session setup")
    print("="*100)

    status, ct, body, resp = try_get(s, f"{BASE}/api/login/channels", "login/channels (to see cookies)")
    if resp:
        print(f"\n  All response headers:")
        for k, v in resp.headers.items():
            print(f"    {k}: {v[:200]}")
        print(f"\n  Session cookies after login/channels:")
        for c in s.cookies:
            print(f"    {c.name} = {c.value[:50]}... (domain={c.domain})")

    # ===== Step 2: Try login/change-channel =====
    print("\n\n" + "="*100)
    print("STEP 2: Try login/change-channel (GET) to activate the channel")
    print("="*100)

    status, ct, body, resp = try_get(s, f"{BASE}/api/login/change-channel?channelNo={CHANNEL_NO}", "login/change-channel")
    if resp:
        print(f"\n  Response headers after change-channel:")
        for k, v in resp.headers.items():
            print(f"    {k}: {v[:200]}")
        print(f"\n  Cookies after change-channel:")
        for c in s.cookies:
            print(f"    {c.name} = {c.value[:50]}... (domain={c.domain})")

    # ===== Step 3: After channel change, try the endpoints again =====
    print("\n\n" + "="*100)
    print("STEP 3: Try endpoints AFTER channel change")
    print("="*100)

    endpoints = [
        (f"{BASE}/api/seller/info", "seller/info"),
        (f"{BASE}/api/sellers", "sellers"),
        (f"{BASE}/api/myconfigs", "myconfigs"),
        (f"{BASE}/api/products/list", "products/list"),
        (f"{BASE}/api/channel-products/list", "channel-products/list"),
        (f"{BASE}/api/dashboards/modals", "dashboards/modals"),
        (f"{BASE}/api/sales-day/with-from-to?fromDateString={month_ago}&toDateString={today}", "sales-day/with-from-to"),
        (f"{BASE}/api/categories", "categories"),
        (f"{BASE}/api/v3/contents/reviews/search", "reviews/search"),
        (f"{BASE}/api/v3/contents/reviews/dash-board/review-count", "review-count"),
    ]

    for url, label in endpoints:
        try_get(s, url, f"{label} (after channel change)")

    # ===== Step 4: Try with login/init (maybe needed to initialize) =====
    print("\n\n" + "="*100)
    print("STEP 4: Check login/init patterns")
    print("="*100)

    # Look at what login/init might expect
    # From the app.js, loginInit is called with channelNo
    status, ct, body, resp = try_get(s, f"{BASE}/api/login/init?channelNo={CHANNEL_NO}", "login/init?channelNo")

    # Also try the login/check
    status, ct, body, resp = try_get(s, f"{BASE}/api/login/check?channelNo={CHANNEL_NO}", "login/check?channelNo")

    # ===== Step 5: Look for the change-channel in app.js =====
    print("\n\n" + "="*100)
    print("STEP 5: Find change-channel usage in app.js")
    print("="*100)

    r = s.get(f"{BASE}/app.js?f3dfd2e83632f6ec00be", timeout=30)
    app_js = r.text

    # Find change-channel patterns
    patterns = [
        r'change-channel[^}]{0,500}',
        r'changeChannel[^}]{0,500}',
        r'loginInit[^}]{0,500}',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, app_js)
        if matches:
            print(f"\n--- Pattern: {pattern[:30]}... ({len(matches)} matches) ---")
            for m in matches[:5]:
                print(f"  {m[:400]}")

    # ===== Step 6: Try seller/info with ssnShow as POST (maybe some endpoints need POST) =====
    print("\n\n" + "="*100)
    print("STEP 6: Check if /api/login/change-channel is POST-only")
    print("="*100)

    # The earlier login/change-channel GET returned BAD_REQUEST - it might need POST
    # But we're read-only, so let's try with the login/changeChannelByToken
    try_get(s, f"{BASE}/api/login/changeChannelByToken?channelNo={CHANNEL_NO}", "changeChannelByToken")

    print("\n\nDone!")

if __name__ == "__main__":
    main()
