# Capturing Naver Smart Store Seller Center API Traffic

Step-by-step guide for capturing API traffic from the Naver Smart Store seller center using Chrome DevTools.

## Prerequisites

- Google Chrome (latest stable)
- Logged into Naver Smart Store seller center at `https://sell.smartstore.naver.com/`
- Seller account with active store data (products, orders, etc.)

## Step 1: Open Chrome DevTools

1. Navigate to `https://sell.smartstore.naver.com/` and log in.
2. Open DevTools with one of:
   - **macOS:** `Cmd + Option + I`
   - **Windows/Linux:** `F12` or `Ctrl + Shift + I`
3. Click the **Network** tab.

## Step 2: Configure the Network Tab

Before navigating to any pages, configure the Network tab for optimal capture:

1. **Check "Preserve log"** -- this keeps network entries when the page navigates. The seller center is a single-page application (SPA) with hash-based routing, so this is less critical for in-app navigation but essential if a full page reload occurs.
2. **Check "Disable cache"** -- forces the browser to fetch fresh responses so you capture the actual payloads.
3. **Filter by request type:** Click the **Fetch/XHR** button in the filter bar. This hides CSS, JS, image, and font requests so only API calls are visible.

## Step 3: Identify API Endpoints

The seller center SPA makes JSON API calls to its backend. Look for these patterns:

- **URL prefix:** Most API calls start with `/api/`. This is the strongest signal.
- **Method:** Many data-fetch endpoints use `POST` (not `GET`), sending a JSON request body with search/filter parameters.
- **Response type:** `application/json`.

Click any request in the list to inspect it:

- **Headers** tab: shows the full URL, method, and request headers (including cookies and CSRF tokens).
- **Payload** tab: shows the request body (for POST requests).
- **Preview** tab: shows a formatted JSON tree of the response.
- **Response** tab: shows the raw response text.

### Useful filter tricks

Type into the filter text box at the top of the Network panel:

- `/api/` -- show only API requests
- `-/analytics` -- exclude analytics tracking calls
- `method:POST` -- show only POST requests

## Step 4: Visit Key Pages

Clear the network log before visiting each page (click the clear button or press `Cmd+K` / `Ctrl+L`). Then navigate to each section and observe the API calls.

### Dashboard

- **URL:** `/#/home/dashboard`
- **API calls to look for:**
  - `GET /api/v1/sellers/dashboards/*` -- dashboard summary data (today's orders, sales, etc.)
  - Various widget data endpoints under the dashboards namespace

### Product List

- **URL:** `/#/products/origin-list`
- **API calls to look for:**
  - `POST /api/products/list/search` -- paginated product search with filter/sort parameters in the request body
  - Request body typically includes `page`, `size`, `orderType`, and filter criteria

### Reviews

- **API calls to look for:**
  - `POST /api/v3/contents/reviews/search` -- review search with pagination
  - Request body includes `page`, `size`, and optional filter fields

### Orders

- **URL:** Order management lives in a separate SPA at `/o/v3/`
- **API calls to look for:**
  - Order list and detail endpoints under the `/o/v3/` path
  - Note: this is a different SPA so the URL structure differs from the main seller center

### Session / Auth

- **API calls to look for:**
  - `GET /api/v1/sellers/auths/login/check-neoid-session` -- validates the current session
  - This call fires on page load and can be used to check if the session cookie is still valid

## Step 5: Export as HAR File

Once you have captured the traffic you need:

1. Right-click anywhere in the Network request list.
2. Select **Save all as HAR with content**.
3. Save the `.har` file with a descriptive name, e.g., `smartstore-dashboard-2026-03-26.har`.

The HAR file is a JSON document containing every request and response, including headers, bodies, and timing. You can later parse it with scripts (see `scripts/diff-api.py`).

## Tips

- **Clear before each page.** Click the clear button (`Cmd+K`) before navigating to a new section. This makes it easy to attribute API calls to specific pages.
- **Use "Preserve log" across navigations.** If you want a single HAR covering multiple sections, enable "Preserve log" and visit each page in sequence.
- **Copy as cURL.** Right-click any request and select "Copy > Copy as cURL". This gives you a ready-to-run curl command with all headers and cookies, useful for testing endpoints outside the browser.
- **Watch the Initiator column.** This shows which JS file triggered the request, helping you trace the call back to AngularJS controller code.
- **Check for pagination.** Many endpoints return paginated data. Look at the request body for `page` and `size` fields, and the response for `totalElements` or `totalPages`.
- **Note CSRF tokens.** Some POST endpoints require a CSRF token header. Check request headers for tokens like `X-CSRF-TOKEN` or similar.
- **Re-login if needed.** Sessions expire. If you see 401 or 403 responses, log in again and resume capture.
