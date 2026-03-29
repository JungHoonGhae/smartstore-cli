"""Playwright-based browser login for Naver Smart Store seller center."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

DEFAULT_URL = "https://sell.smartstore.naver.com"
SELLER_CENTER_HOST = "sell.smartstore.naver.com"
REQUIRED_COOKIE_NAMES = {"NID_AUT", "NID_SES"}
POLL_INTERVAL_SEC = 1
MAX_WAIT_SEC = 300
REFRESH_TIMEOUT_SEC = 30


def main() -> None:
    parser = argparse.ArgumentParser(prog="storectl-auth-helper")
    sub = parser.add_subparsers(dest="command")

    login_parser = sub.add_parser("login", help="Open browser for Naver login")
    login_parser.add_argument(
        "--storage-state",
        required=True,
        help="Path to write Playwright storage state JSON",
    )
    login_parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="URL to open after login",
    )
    login_parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (not recommended for login)",
    )

    refresh_parser = sub.add_parser("refresh", help="Headless session refresh using existing cookies")
    refresh_parser.add_argument(
        "--storage-state",
        required=True,
        help="Path to existing Playwright storage state JSON (read + overwrite)",
    )

    args = parser.parse_args()
    if args.command == "login":
        run_login(args)
    elif args.command == "refresh":
        run_refresh(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_login(args: argparse.Namespace) -> None:
    from playwright.sync_api import sync_playwright

    storage_state_path = Path(args.storage_state)
    storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=args.headless, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        page.goto(args.url)

        start = time.time()
        while time.time() - start < MAX_WAIT_SEC:
            cookies = context.cookies()
            cookie_names = {c["name"] for c in cookies}

            if REQUIRED_COOKIE_NAMES.issubset(cookie_names):
                current_url = page.url
                if SELLER_CENTER_HOST in current_url and "nidlogin" not in current_url:
                    time.sleep(3)
                    break

            time.sleep(POLL_INTERVAL_SEC)
        else:
            print(
                json.dumps({"error": "login timed out after {} seconds".format(MAX_WAIT_SEC)}),
                file=sys.stderr,
            )
            browser.close()
            sys.exit(1)

        _save_and_report(context, storage_state_path, "Captured authenticated Naver Smart Store storage state.")
        browser.close()


def run_refresh(args: argparse.Namespace) -> None:
    """Headless refresh: load existing storage state, navigate to seller center, capture new cookies."""
    from playwright.sync_api import sync_playwright

    storage_state_path = Path(args.storage_state)
    if not storage_state_path.exists():
        print(json.dumps({"error": "storage state file not found: {}".format(storage_state_path)}), file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(storage_state=str(storage_state_path))
        page = context.new_page()

        try:
            page.goto(DEFAULT_URL, wait_until="networkidle", timeout=REFRESH_TIMEOUT_SEC * 1000)
        except Exception:
            pass  # timeout is ok, we just need cookies

        # Check if we got a valid session
        cookies = context.cookies()
        cookie_names = {c["name"] for c in cookies}
        current_url = page.url

        if not REQUIRED_COOKIE_NAMES.issubset(cookie_names):
            print(
                json.dumps({"error": "refresh failed: NID cookies not present after navigation"}),
                file=sys.stderr,
            )
            browser.close()
            sys.exit(1)

        if "nidlogin" in current_url:
            print(
                json.dumps({"error": "refresh failed: redirected to login page (NID cookies expired)"}),
                file=sys.stderr,
            )
            browser.close()
            sys.exit(1)

        # Wait for SPA to load and set all cookies
        time.sleep(3)

        _save_and_report(context, storage_state_path, "Session refreshed (headless).")
        browser.close()


def _save_and_report(context, storage_state_path: Path, message: str) -> None:
    storage_state = context.storage_state()
    storage_state_path.write_text(json.dumps(storage_state, indent=2))

    cookie_count = len(storage_state.get("cookies", []))
    origin_count = len(storage_state.get("origins", []))

    result = {
        "status": "ok",
        "message": message,
        "storage_state_path": str(storage_state_path),
        "cookie_count": cookie_count,
        "origin_count": origin_count,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
