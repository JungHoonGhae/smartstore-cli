# Advanced API Capture with mitmproxy

Guide for using mitmproxy to intercept and analyze Naver Smart Store seller center traffic. This approach is useful for capturing traffic from non-browser clients or for automated, scriptable interception.

## Prerequisites

- macOS, Linux, or Windows
- Python 3.9+ (for addon scripts)
- A browser you can configure to use a proxy

## Installing mitmproxy

### macOS (Homebrew)

```bash
brew install mitmproxy
```

### pip (any platform)

```bash
pip install mitmproxy
```

### Verify installation

```bash
mitmproxy --version
```

## Setting Up the CA Certificate

mitmproxy generates its own Certificate Authority (CA) to decrypt HTTPS traffic. You must trust this CA on your system.

### 1. Start mitmproxy once to generate the CA

```bash
mitmproxy
```

Press `q` then `y` to quit. The CA files are now at `~/.mitmproxy/`.

### 2. Install the CA certificate

#### macOS

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  ~/.mitmproxy/mitmproxy-ca-cert.pem
```

Or open `~/.mitmproxy/mitmproxy-ca-cert.pem` in Finder, which launches Keychain Access. Set the certificate to "Always Trust".

#### Linux (Debian/Ubuntu)

```bash
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates
```

### 3. Verify in browser

Configure your browser to use `127.0.0.1:8080` as its HTTP/HTTPS proxy, then visit `http://mitm.it`. You should see a page confirming the proxy is active.

## Running mitmproxy

### Interactive TUI

```bash
mitmproxy --listen-port 8080
```

This opens an interactive terminal UI where you can inspect requests in real time.

### Web interface

```bash
mitmweb --listen-port 8080
```

This opens a web-based UI at `http://127.0.0.1:8081` -- easier for browsing large captures.

### Dump mode (headless)

```bash
mitmdump --listen-port 8080 -w capture.flow
```

Writes all traffic to a flow file for later analysis.

## Configuring Chrome to Use the Proxy

Launch Chrome with the proxy flag:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --proxy-server="127.0.0.1:8080" \
  --user-data-dir="/tmp/chrome-mitmproxy"
```

Using `--user-data-dir` creates a separate Chrome profile so your normal browsing is not affected.

Then log into the Naver Smart Store seller center as usual.

## Filtering for Smart Store Traffic

### URL filter in mitmproxy TUI

Press `f` to set a filter expression:

```
~d sell.smartstore.naver.com & ~u /api/
```

This shows only requests to `sell.smartstore.naver.com` that contain `/api/` in the URL.

### Common filter expressions

| Filter | Meaning |
|--------|---------|
| `~d sell.smartstore.naver.com` | Domain filter |
| `~u /api/` | URL contains `/api/` |
| `~m POST` | POST requests only |
| `~c 200` | Response code 200 |
| `~t application/json` | JSON content type |
| `~b "totalElements"` | Response body contains string |

Combine with `&` (and), `\|` (or), `!` (not).

## Addon Script for Smart Store

Create a Python addon script to automatically filter and log Smart Store API calls.

Save as `scripts/mitmproxy-smartstore.py`:

```python
"""
mitmproxy addon that logs Naver Smart Store API calls.

Usage:
    mitmproxy -s scripts/mitmproxy-smartstore.py
    mitmdump -s scripts/mitmproxy-smartstore.py -w smartstore.flow
"""

import json
import logging
from mitmproxy import http, ctx

SMARTSTORE_HOSTS = [
    "sell.smartstore.naver.com",
    "sell.store.naver.com",
]

API_PREFIX = "/api/"


class SmartStoreLogger:
    def __init__(self):
        self.api_calls = []

    def response(self, flow: http.HTTPFlow) -> None:
        if flow.request.host not in SMARTSTORE_HOSTS:
            return
        if API_PREFIX not in flow.request.path:
            return

        entry = {
            "method": flow.request.method,
            "url": flow.request.url,
            "path": flow.request.path,
            "status": flow.response.status_code,
            "request_content_type": flow.request.headers.get("content-type", ""),
            "response_content_type": flow.response.headers.get("content-type", ""),
        }

        # Log request body for POST
        if flow.request.method == "POST" and flow.request.content:
            try:
                entry["request_body"] = json.loads(flow.request.content)
            except (json.JSONDecodeError, UnicodeDecodeError):
                entry["request_body"] = "<non-JSON>"

        # Log response body structure (keys only, not values)
        if flow.response.content:
            try:
                resp = json.loads(flow.response.content)
                if isinstance(resp, dict):
                    entry["response_keys"] = list(resp.keys())
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        self.api_calls.append(entry)
        ctx.log.info(
            f"[smartstore] {entry['method']} {entry['path']} -> {entry['status']}"
        )

    def done(self):
        ctx.log.info(f"[smartstore] Total API calls captured: {len(self.api_calls)}")
        if self.api_calls:
            output_path = "smartstore-api-calls.json"
            with open(output_path, "w") as f:
                json.dump(self.api_calls, f, indent=2, ensure_ascii=False)
            ctx.log.info(f"[smartstore] Saved to {output_path}")


addons = [SmartStoreLogger()]
```

### Running with the addon

```bash
# Interactive
mitmproxy -s scripts/mitmproxy-smartstore.py

# Headless with flow file
mitmdump -s scripts/mitmproxy-smartstore.py -w smartstore.flow
```

When you quit mitmproxy (press `q` in TUI, or `Ctrl+C` for mitmdump), the addon writes all captured API calls to `smartstore-api-calls.json`.

## Saving and Replaying Captures

### Save to flow file

```bash
mitmdump --listen-port 8080 -w capture.flow
```

### Read back a flow file

```bash
# View in TUI
mitmproxy -r capture.flow

# View in web UI
mitmweb -r capture.flow

# Replay to a file
mitmdump -r capture.flow -w filtered.flow "~u /api/"
```

### Export to HAR

mitmproxy can export captures to HAR format for use with `scripts/diff-api.py`:

```bash
mitmdump -r capture.flow --set hardump=capture.har
```

## Cleanup

When you are finished, remove the mitmproxy CA from your system trust store:

### macOS

Open Keychain Access, search for "mitmproxy", and delete the certificate.

### Linux

```bash
sudo rm /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates
```

## Security Reminder

- Never leave the mitmproxy CA certificate trusted on a production machine.
- The CA private key at `~/.mitmproxy/mitmproxy-ca.pem` can decrypt any HTTPS traffic on your machine if the CA is trusted. Keep it safe.
- Only use mitmproxy on your own accounts and traffic. Intercepting others' traffic without consent is illegal.
