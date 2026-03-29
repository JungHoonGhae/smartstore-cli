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
  domain/           Data models
  output/           Multi-format renderers (table/JSON/CSV)
  session/          Browser session persistence
  version/          Build version info
auth-helper/        Python + Playwright login helper
schemas/            JSON Schema for config.json
```

## Commands

- `storectl version` — Show version info
- `storectl doctor` — System health check
- `storectl config init|show` — Config management
- `storectl auth login|status|logout|doctor` — Session management
- `storectl product list|show <id>` — Product data
- `storectl order list [--status pending|completed|all]|show <id>` — Order data
- `storectl stats daily [--date YYYY-MM-DD]|monthly [--month YYYY-MM]` — Sales stats
- `storectl settlement list [--month YYYY-MM]` — Settlement data
- `storectl inquiry list [--status all|pending|answered]` — Customer inquiries
- `storectl review list` — Product reviews

## Conventions

- All commands are read-only by default
- Every domain command supports `--output table|json|csv`
- Config stored in `~/.config/storectl/`
- Session stored in `~/.config/storectl/session.json`
