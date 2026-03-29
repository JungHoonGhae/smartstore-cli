# smartstore-cli

Unofficial Naver Smart Store (스마트스토어/스토어팜) CLI for seller center data access.

## Binary

`storectl` — the single CLI binary produced by `cmd/storectl/`.

## Tech Stack

- **Language:** Go 1.25+
- **CLI framework:** spf13/cobra
- **Browser automation:** Python + Playwright (login only)
- **Output formats:** table, JSON, CSV

## Build & Run

```bash
make build          # → bin/storectl
make run            # go run
make test           # go test ./...
make fmt            # gofmt
make tidy           # go mod tidy
```

## Project Layout

```
cmd/storectl/       CLI command layer (Cobra commands)
internal/
  auth/             Browser login orchestration
  client/           Naver Smart Store web API client
  config/           Configuration loading & paths
  doctor/           System health check
  domain/           Data models (mapped to real API responses)
  output/           Multi-format renderers (table/JSON/CSV)
  session/          Browser session persistence with auto-refresh
  version/          Build version info
auth-helper/        Python + Playwright login helper
docs/               API documentation & capture guides
fixtures/           Captured API response samples
schemas/            JSON Schema for config.json
scripts/            API discovery & analysis tools
```

## Commands

### System
- `storectl version` — Show version info
- `storectl doctor` — System health check
- `storectl config init|show` — Config management

### Auth
- `storectl auth login` — Browser-assisted login (Playwright)
- `storectl auth status` — Session state (includes Last Used At)
- `storectl auth refresh` — Headless session refresh
- `storectl auth logout` — Clear session
- `storectl auth doctor` — Check auth prerequisites

### Data (Read-Only)
- `storectl seller info` — Store info (name, URL, representative, bank)
- `storectl seller grade` — Seller grade + penalties
- `storectl product list [--page N] [--size N]` — Product search (paginated)
- `storectl product show <id>` — Product detail (by channel product no)
- `storectl product dashboard` — Product count summary
- `storectl order list` — Order/delivery dashboard
- `storectl order list --detail [--page N] [--size N]` — Order list (GraphQL)
- `storectl stats daily` — Sales summary (daily/weekly/monthly)
- `storectl settlement list` — Settlement dashboard
- `storectl inquiry list` — Customer inquiries
- `storectl review list [--page N] [--size N]` — Review search (paginated)
- `storectl review dashboard` — Review count summary
- `storectl notification list [--count N]` — Notifications

## Real API Endpoints

Reverse-engineered from the seller center AngularJS SPA:

| Pattern | Method | Usage |
|---------|--------|-------|
| `/api/v1/sellers/dashboards/*` | GET | Dashboard data (orders, products, settlement, reviews) |
| `/api/products/list/search` | POST | Product search (requires searchKeywordType, searchOrderType) |
| `/api/v3/contents/reviews/search` | POST | Review search (paginated) |
| `/api/channels?_action=selectedChannel` | GET | Seller/channel info |
| `/api/v1/sellers/dashboards/seller-grade` | GET | Seller grade |
| `/api/seller/notification/user-activities/counts` | GET | Notification counts |
| `/api/seller/notification/user-activities` | GET | Notification activities |
| `/api/login/channels` | GET | Available channels |
| `/api/login/change-channel` | POST | Channel selection (session init) |
| `/api/login/init` | GET | Session initialization |
| `/o/v3/graphql` | POST | Order list (separate SPA, Apollo) |

## Session Management

- Session persisted in `session.json` with cookies, headers, localStorage
- Auto cookie refresh from Set-Cookie response headers
- Auto session init (change-channel + login/init) on AuthError
- Auto session refresh via Playwright on persistent failure
- `LastUsedAt` tracked for expiry estimation
- Cookie quote stripping for Go net/http compatibility (CBI_CHK fix)

## Conventions

- All commands are read-only by default
- Every domain command supports `--output table|json|csv`
- Config dir: `~/Library/Application Support/storectl/` (macOS) or `~/.config/storectl/` (Linux)
- Session file: `<config-dir>/session.json`
- Rate limiter: 200ms minimum between API requests
