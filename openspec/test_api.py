#!/usr/bin/env python3
"""Test Naver Smart Store Seller Center API endpoints.

Uses Playwright to create a browser session with saved cookies.
Uses page.evaluate(fetch) for API calls within the browser's cookie context.
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = "https://sell.smartstore.naver.com"
SESSION_PATH = "/Users/junghoon/Library/Application Support/storectl/session.json"
OUTPUT_PATH = "/Users/junghoon/workspace/projects/oss-smartstore-cli/openspec/api-responses.md"


def load_session():
    with open(SESSION_PATH, "r") as f:
        return json.load(f)


def truncate_json(obj, max_chars=2000):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if len(text) > max_chars:
        return text[:max_chars] + "\n... (truncated)"
    return text


def call_via_fetch(page, method, path, body=None, label=""):
    """Execute fetch() in the browser context."""
    if path.startswith("http"):
        url = path
        display_path = path.replace(BASE_URL, "")
    else:
        url = BASE_URL + path
        display_path = path

    print(f"\n{'=' * 80}")
    print(f"[{label}] {method} {display_path}")
    print(f"{'=' * 80}")

    try:
        body_str = json.dumps(body) if body else "null"
        result = page.evaluate("""
        async ([url, method, bodyStr]) => {
            const fetchOpts = {
                method: method,
                credentials: "include",
                headers: { "Accept": "application/json" },
            };
            if (bodyStr !== "null") {
                fetchOpts.headers["Content-Type"] = "application/json;charset=UTF-8";
                fetchOpts.body = bodyStr;
            }
            try {
                const resp = await fetch(url, fetchOpts);
                const text = await resp.text();
                let parsed;
                try { parsed = JSON.parse(text); } catch(e) { parsed = text || "(empty)"; }
                return { status: resp.status, body: parsed };
            } catch(e) {
                return { status: "FETCH_ERROR", body: e.message };
            }
        }
        """, [url, method, body_str])

        status = result["status"]
        data = result["body"]
        print(f"Status: {status}")
        if isinstance(data, (dict, list)):
            pretty = truncate_json(data)
        else:
            pretty = str(data)[:2000] if data else "(empty)"
        print(pretty)
        return {
            "label": label, "method": method, "path": display_path,
            "status": status, "response": pretty, "body": body,
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "label": label, "method": method, "path": display_path,
            "status": "ERROR", "response": str(e), "body": body,
        }


def main():
    session_data = load_session()
    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()

        # Inject saved cookies
        cookies_for_pw = []
        for name, value in session_data["cookies"].items():
            if name.startswith("NID") or name in (
                "NNB", "nid_buk", "nid_inf", "nid_slevel",
                "NAC", "NACT", "NEONB", "SRT30", "SRT5",
            ):
                domain = ".naver.com"
            else:
                domain = ".smartstore.naver.com"
            cookies_for_pw.append({
                "name": name, "value": value, "domain": domain,
                "path": "/", "httpOnly": False, "secure": True, "sameSite": "None",
            })
        context.add_cookies(cookies_for_pw)

        page = context.new_page()
        print("*** Loading seller center... ***")
        page.goto(BASE_URL + "/", wait_until="networkidle", timeout=30000)
        print(f"Page URL: {page.url}")

        if "nidlogin" in page.url or "accounts" in page.url:
            print("!!! Session expired !!!")
            browser.close()
            with open(OUTPUT_PATH, "w") as f:
                f.write("# Session Expired\n\nRun `storectl auth login` to refresh.\n")
            return

        print("Session valid!")
        time.sleep(2)

        # --- Auth Flow ---
        r = call_via_fetch(page, "GET", "/api/login/channels", label="Login Channels")
        results.append(r)

        channel_no, role_no = 1100114368, 200206319
        try:
            ch = page.evaluate("""async () => {
                const r = await fetch("/api/login/channels", {
                    credentials: "include", headers: {"Accept": "application/json"}
                });
                return await r.json();
            }""")
            if isinstance(ch, list) and len(ch) > 0:
                channel_no = ch[0].get("channelNo", channel_no)
                role_no = ch[0].get("roleNo", role_no)
        except:
            pass
        print(f">>> channelNo={channel_no}, roleNo={role_no}")

        r = call_via_fetch(page, "POST",
            f"/api/login/change-channel?roleNo={role_no}&channelNo={channel_no}&url=/",
            label="Change Channel")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/login/init?stateName=home.dashboard&needLoginInfoForAngular=true",
            label="Login Init")
        results.append(r)
        time.sleep(1)

        # --- Original requested endpoints ---
        r = call_via_fetch(page, "GET", "/api/dashboards/pay/sale-stats",
                           label="Dashboard Sale Stats")
        results.append(r)

        r = call_via_fetch(page, "GET", "/api/dashboards/pay/order-delivery",
                           label="Dashboard Order Delivery")
        results.append(r)

        r = call_via_fetch(page, "GET", "/api/dashboards/channel/products",
                           label="Dashboard Channel Products")
        results.append(r)

        r = call_via_fetch(page, "GET", "/api/dashboards/pay/settlement",
                           label="Dashboard Settlement")
        results.append(r)

        r = call_via_fetch(page, "GET", "/api/v3/contents/reviews/dash-board/review-count",
                           label="Review Count")
        results.append(r)

        r = call_via_fetch(page, "POST", "/api/channel-products/list/search",
            body={
                "searchOrderType": "RECENTLY_REGISTERED",
                "searchKeywordType": "ALL",
                "page": 1, "pageSize": 10,
                "searchChannelProductDisplayStatusTypes": [],
            },
            label="Channel Product List Search")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/sales-day/with-from-to?fromDateString=20260301&toDateString=20260326",
            label="Daily Sales (legacy)")
        results.append(r)

        r = call_via_fetch(page, "GET", "/api/seller/info",
                           label="Seller Info (legacy)")
        results.append(r)

        # --- Working v1 alternatives for failed endpoints ---
        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/account/sales-summary-full-chart?isRefresh=true",
            label="Sales Summary Full Chart (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/pay/order-delivery",
            label="Order Delivery (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/pay/settlement",
            label="Settlement (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/channel/products",
            label="Channel Products (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/reviews",
            label="Dashboard Reviews (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/inquiries",
            label="Dashboard Inquiries (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/seller-grade",
            label="Seller Grade (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            f"/api/v1/sellers/dashboards/channel/store-customer-status?channelNo={channel_no}&withChannelInfo=true",
            label="Store Customer Status (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/pay/claim",
            label="Dashboard Claims (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/good-service-score",
            label="Good Service Score (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/account/penalties",
            label="Account Penalties (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/group-product-info",
            label="Group Product Info (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/ranking-diagnosis",
            label="Ranking Diagnosis (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/product-diagnosis",
            label="Product Diagnosis (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/dashboards/onboarding",
            label="Onboarding (v1)")
        results.append(r)

        r = call_via_fetch(page, "GET",
            "/api/v1/sellers/context/for-resource-menu",
            label="Seller Context / Menu (v1)")
        results.append(r)

        # Save refreshed session cookies
        all_cookies = context.cookies()
        refreshed_cookies = {}
        for c in all_cookies:
            refreshed_cookies[c["name"]] = c["value"]
        if refreshed_cookies:
            new_session = {
                "provider": "playwright",
                "cookies": refreshed_cookies,
                "headers": {"Referer": "https://sell.smartstore.naver.com/"},
                "storage": session_data.get("storage", {}),
                "retrieved_at": datetime.utcnow().isoformat() + "Z",
            }
            with open(SESSION_PATH, "w") as f:
                json.dump(new_session, f, indent=2)
            print(f"\n>>> Refreshed session saved with {len(refreshed_cookies)} cookies")

        browser.close()

    # Write results to markdown
    with open(OUTPUT_PATH, "w") as f:
        f.write("# Naver Smart Store API Response Log\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write("---\n\n")

        for r in results:
            if r is None:
                continue
            f.write(f"## {r['label']}\n\n")
            f.write(f"- **Endpoint:** `{r['method']} {r['path']}`\n")
            f.write(f"- **Status:** `{r['status']}`\n")
            if r.get("body"):
                f.write(f"- **Request Body:** `{json.dumps(r['body'])}`\n")
            f.write(f"\n**Response:**\n\n```json\n{r['response']}\n```\n\n---\n\n")

    print(f"\n\n{'#' * 80}")
    print(f"Results saved to: {OUTPUT_PATH}")
    print(f"{'#' * 80}")


if __name__ == "__main__":
    main()
