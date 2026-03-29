#!/usr/bin/env python3
"""
Compare two HAR files and report API endpoint differences.

Usage:
    python3 scripts/diff-api.py old.har new.har

Extracts all API endpoints (URLs containing '/api/') from each HAR file
and reports:
    - New endpoints (present in new but not old)
    - Removed endpoints (present in old but not new)
    - Changed response structures (different top-level JSON keys)
"""

import json
import sys
from collections import defaultdict
from urllib.parse import urlparse, parse_qs


def load_har(path: str) -> dict:
    """Load and parse a HAR file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_path(url: str) -> str:
    """Extract the path from a URL, stripping query parameters.

    Returns just the path component, e.g.:
        https://sell.smartstore.naver.com/api/v1/sellers/dashboards/summary?x=1
        -> /api/v1/sellers/dashboards/summary
    """
    parsed = urlparse(url)
    return parsed.path


def extract_api_entries(har: dict) -> dict[str, list[dict]]:
    """Extract API entries from a HAR file.

    Returns a dict mapping (METHOD path) -> list of response info dicts.
    Only includes entries whose URL path contains '/api/'.
    """
    entries_by_endpoint = defaultdict(list)

    for entry in har.get("log", {}).get("entries", []):
        request = entry.get("request", {})
        response = entry.get("response", {})

        url = request.get("url", "")
        method = request.get("method", "GET")
        path = normalize_path(url)

        if "/api/" not in path:
            continue

        endpoint_key = f"{method} {path}"

        # Try to parse response body as JSON to get structure
        response_keys = None
        content = response.get("content", {})
        text = content.get("text", "")
        if text:
            try:
                body = json.loads(text)
                if isinstance(body, dict):
                    response_keys = sorted(body.keys())
            except (json.JSONDecodeError, TypeError):
                pass

        # Try to parse request body for POST endpoints
        request_keys = None
        post_data = request.get("postData", {})
        post_text = post_data.get("text", "")
        if post_text:
            try:
                req_body = json.loads(post_text)
                if isinstance(req_body, dict):
                    request_keys = sorted(req_body.keys())
            except (json.JSONDecodeError, TypeError):
                pass

        entries_by_endpoint[endpoint_key].append(
            {
                "status": response.get("status"),
                "response_keys": response_keys,
                "request_keys": request_keys,
            }
        )

    return dict(entries_by_endpoint)


def get_representative_keys(entries: list[dict]) -> set[str] | None:
    """Get the union of all response keys across entries for an endpoint."""
    all_keys = set()
    has_any = False
    for entry in entries:
        if entry["response_keys"] is not None:
            has_any = True
            all_keys.update(entry["response_keys"])
    return all_keys if has_any else None


def diff_apis(old_path: str, new_path: str) -> None:
    """Compare two HAR files and print the diff."""
    old_har = load_har(old_path)
    new_har = load_har(new_path)

    old_entries = extract_api_entries(old_har)
    new_entries = extract_api_entries(new_har)

    old_endpoints = set(old_entries.keys())
    new_endpoints = set(new_entries.keys())

    added = sorted(new_endpoints - old_endpoints)
    removed = sorted(old_endpoints - new_endpoints)
    common = sorted(old_endpoints & new_endpoints)

    # --- New Endpoints ---
    print("=" * 60)
    print("NEW ENDPOINTS")
    print("=" * 60)
    if added:
        for ep in added:
            print(f"  + {ep}")
            keys = get_representative_keys(new_entries[ep])
            if keys:
                print(f"    response keys: {', '.join(sorted(keys))}")
    else:
        print("  (none)")
    print()

    # --- Removed Endpoints ---
    print("=" * 60)
    print("REMOVED ENDPOINTS")
    print("=" * 60)
    if removed:
        for ep in removed:
            print(f"  - {ep}")
            keys = get_representative_keys(old_entries[ep])
            if keys:
                print(f"    response keys: {', '.join(sorted(keys))}")
    else:
        print("  (none)")
    print()

    # --- Changed Response Structures ---
    print("=" * 60)
    print("CHANGED RESPONSE STRUCTURES")
    print("=" * 60)
    changes_found = False
    for ep in common:
        old_keys = get_representative_keys(old_entries[ep])
        new_keys = get_representative_keys(new_entries[ep])

        if old_keys is None or new_keys is None:
            continue

        if old_keys != new_keys:
            changes_found = True
            added_keys = sorted(new_keys - old_keys)
            removed_keys = sorted(old_keys - new_keys)

            print(f"  ~ {ep}")
            if added_keys:
                print(f"    + added keys:   {', '.join(added_keys)}")
            if removed_keys:
                print(f"    - removed keys: {', '.join(removed_keys)}")

    if not changes_found:
        print("  (none)")
    print()

    # --- Summary ---
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Old HAR: {old_path}")
    print(f"    Endpoints: {len(old_endpoints)}")
    print(f"  New HAR: {new_path}")
    print(f"    Endpoints: {len(new_endpoints)}")
    print()
    print(f"  New:     {len(added)}")
    print(f"  Removed: {len(removed)}")
    print(f"  Changed: {sum(1 for _ in filter(None, [True] if changes_found else []))}")
    print()


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/diff-api.py <old.har> <new.har>", file=sys.stderr)
        print()
        print("Compare two HAR files and show API endpoint differences.", file=sys.stderr)
        print()
        print("Arguments:", file=sys.stderr)
        print("  old.har    Path to the older HAR file (baseline)", file=sys.stderr)
        print("  new.har    Path to the newer HAR file (to compare)", file=sys.stderr)
        sys.exit(1)

    old_path = sys.argv[1]
    new_path = sys.argv[2]

    try:
        diff_apis(old_path, new_path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in HAR file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
