# smartstore-cli

[![Status](https://img.shields.io/badge/status-beta-orange)]()
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Unofficial Naver Smart Store (스마트스토어/스토어팜) CLI for seller center data access.

> **Warning**: This is not an official Naver product. It uses unofficial internal web APIs
> that may change without notice. The developer assumes no responsibility for account
> restrictions or any damages arising from its use.

## Quick Start

```bash
# Install from source
git clone https://github.com/JungHoonGhae/smartstore-cli.git
cd smartstore-cli
make build

# Install auth helper (Python 3.10+)
pip install -e auth-helper/
playwright install chromium

# Check prerequisites
bin/storectl doctor

# Login via browser
bin/storectl auth login

# Try it
bin/storectl seller info
bin/storectl order list --output json
```

## Features

### Read-Only (조회)

| Command | Description |
|---------|-------------|
| `storectl seller info` | 스토어 정보 (스토어명, URL, 대표자, 연락처, 정산계좌) |
| `storectl seller grade` | 판매자 등급 + 페널티 |
| `storectl product list [--page N] [--size N]` | 상품 목록 (페이지네이션) |
| `storectl product show <id>` | 상품 상세 |
| `storectl product dashboard` | 상품 현황 카운트 |
| `storectl order list` | 주문/배송 대시보드 |
| `storectl order list --detail` | 주문 목록 상세 (GraphQL) |
| `storectl stats daily` | 매출 통계 (일간/주간/월간) |
| `storectl settlement list` | 정산 대시보드 |
| `storectl inquiry list` | 고객 문의 |
| `storectl review list [--page N] [--size N]` | 리뷰 목록 (페이지네이션) |
| `storectl review dashboard` | 리뷰 대시보드 |
| `storectl notification list [--count N]` | 알림 목록 |

### System

| Command | Description |
|---------|-------------|
| `storectl version` | 버전 정보 |
| `storectl doctor` | 시스템 건강 체크 |
| `storectl config init\|show` | 설정 관리 |
| `storectl auth login` | 브라우저 기반 로그인 |
| `storectl auth status` | 세션 상태 확인 |
| `storectl auth refresh` | 세션 갱신 (headless) |
| `storectl auth logout` | 세션 삭제 |
| `storectl auth doctor` | 인증 요구사항 점검 |

### Output Formats

모든 데이터 커맨드는 `--output` 플래그를 지원합니다:

```bash
storectl seller info --output json
storectl product list --output csv
storectl order list --output table   # default
```

## How It Works

```
User → storectl auth login
         ↓
       Python Playwright → Opens Chromium browser
         ↓
       User completes Naver ID login
         ↓
       Captures cookies (NID_AUT, NID_SES, kit.session, ...)
         ↓
       Saves to session.json
         ↓
User → storectl product list
         ↓
       Loads session.json → Applies cookies to HTTP request
         ↓
       POST https://sell.smartstore.naver.com/api/products/list/search
         ↓
       Parses JSON → Renders table/json/csv
```

### Session Management

- 세션은 `session.json`에 저장되며 API 호출마다 자동으로 쿠키를 갱신합니다
- 세션 만료 시 자동으로 `change-channel` + `login/init` 플로우를 시도합니다
- `storectl auth status`에서 마지막 사용 시각과 세션 상태를 확인할 수 있습니다
- 자동 갱신 실패 시 `storectl auth login`으로 재로그인이 필요합니다

## API Architecture

네이버 스마트스토어 판매자센터는 AngularJS SPA로 구성되어 있으며, 내부적으로 다음 API를 사용합니다:

| API Pattern | Usage |
|-------------|-------|
| `GET /api/v1/sellers/dashboards/*` | 대시보드 데이터 (주문, 상품, 정산, 리뷰 등) |
| `POST /api/products/list/search` | 상품 검색 |
| `POST /api/v3/contents/reviews/search` | 리뷰 검색 |
| `GET /api/channels?_action=selectedChannel` | 판매자/채널 정보 |
| `POST /o/v3/graphql` | 주문 상세 (별도 SPA) |
| `POST /api/login/change-channel` | 세션 초기화 |

## Installation

### From Source

```bash
git clone https://github.com/JungHoonGhae/smartstore-cli.git
cd smartstore-cli
make build
```

### Auth Helper

Python 3.10+ 필요:

```bash
pip install -e auth-helper/
playwright install chromium
```

### Prerequisites Check

```bash
bin/storectl doctor
```

정상이면:
```
[ok] python_binary
[ok] auth_helper_dir
[ok] playwright_module
[ok] chromium_installed
```

## Development

```bash
make build     # → bin/storectl
make test      # go test ./...
make fmt       # gofmt
make tidy      # go mod tidy
make clean     # rm bin/ coverage.out
```

### Project Layout

```
cmd/storectl/        CLI command layer (Cobra)
internal/
  auth/              Browser login orchestration
  client/            Naver Smart Store web API client
  config/            Configuration loading & paths
  doctor/            System health check
  domain/            Data models (mapped to real API responses)
  output/            Multi-format renderers (table/JSON/CSV)
  session/           Session persistence with auto-refresh
  version/           Build version info
auth-helper/         Python + Playwright login helper
docs/                API documentation & capture guides
fixtures/            Captured API response samples
schemas/             JSON Schema for config.json
scripts/             API discovery & analysis tools
```

### Reverse Engineering

API 엔드포인트는 브라우저 트래픽 캡처를 통해 리버스 엔지니어링되었습니다:

- `docs/reverse-engineering/capture-guide.md` — Chrome DevTools 캡처 가이드
- `docs/reverse-engineering/mitmproxy-guide.md` — mitmproxy 고급 가이드
- `docs/api/CHANGELOG.md` — API 변경 이력

## Local Storage

| File | Purpose |
|------|---------|
| `<config-dir>/config.json` | 설정 파일 |
| `<config-dir>/session.json` | 브라우저 세션 (쿠키, 헤더, localStorage) |

Config directory: `~/Library/Application Support/storectl/` (macOS) or `~/.config/storectl/` (Linux)

## License

MIT License - see [LICENSE](LICENSE) for details.
