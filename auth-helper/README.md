# storectl-auth-helper

Python-based browser login helper for `storectl auth login`.

## Responsibilities

- Open a real browser session (Google Chrome via Playwright)
- Let user complete Naver Smart Store seller center web login
- Extract minimum session state needed by Go client
- Return sanitized session payload to storectl

## Hard Boundary (What It Does NOT Do)

- No Naver Smart Store domain logic
- No read-only client bindings
- No product/order manipulation
- Isolates browser automation from main CLI

## Usage

```bash
cd auth-helper
python3 -m pip install -e .
python3 -m storectl_auth_helper login --storage-state /tmp/storectl-storage-state.json
```

## Requirements

- Python 3.11+
- Google Chrome installed on system
- `playwright install chromium` is NOT needed (uses system Chrome via `channel="chrome"`)

## Output

JSON on stdout:
```json
{
  "status": "ok",
  "message": "Captured authenticated Naver Smart Store storage state.",
  "storage_state_path": "/tmp/storectl-storage-state.json",
  "cookie_count": 17,
  "origin_count": 3
}
```
