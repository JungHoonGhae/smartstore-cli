<div align="center">
  <h1>smartstore-cli</h1>
  <p>네이버 스마트스토어 판매자센터 웹 세션을 재사용해 조회 데이터를 터미널에서 다루기 위한 비공식 CLI입니다.</p>
  <p>실행 바이너리는 <code>storectl</code>입니다.</p>
</div>

<p align="center">
  <a href="#quick-start"><strong>Quick Start</strong></a> ·
  <a href="#지원-범위"><strong>지원 범위</strong></a> ·
  <a href="#how-it-works"><strong>How It Works</strong></a> ·
  <a href="#development"><strong>Development</strong></a> ·
  <a href="#문서"><strong>문서</strong></a>
</p>

<p align="center">
  <a href="https://github.com/JungHoonGhae/smartstore-cli/stargazers"><img src="https://img.shields.io/github/stars/JungHoonGhae/smartstore-cli" alt="GitHub stars" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License" /></a>
  <a href="https://go.dev/"><img src="https://img.shields.io/badge/Go-1.25+-00ADD8.svg" alt="Go" /></a>
  <a href="https://github.com/JungHoonGhae/smartstore-cli"><img src="https://img.shields.io/badge/status-beta-orange.svg" alt="Status Beta" /></a>
  <a href="https://github.com/JungHoonGhae/smartstore-cli/actions/workflows/ci.yml"><img src="https://github.com/JungHoonGhae/smartstore-cli/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
</p>

> [!WARNING]
> 이 프로젝트는 네이버 공식 제품이 아닙니다. 웹 내부 API를 비공식적으로 사용하며, 네이버 이용약관(TOS) 위반에 해당할 수 있습니다. API는 예고 없이 변경될 수 있고, 사용으로 인한 계정 제한, 손실, 기타 불이익에 대해 개발자는 어떠한 책임도 지지 않습니다. 본인의 판단과 책임 하에 사용하세요.

> [!IMPORTANT]
> 모든 커맨드는 **읽기 전용(read-only)** 입니다. 상품 등록/수정, 주문 상태 변경 등 쓰기 작업은 지원하지 않습니다.

<div align="center">
<table>
  <tr>
    <td align="center"><strong>Works with</strong></td>
    <td align="center"><img src="docs/assets/logos/claude.svg" width="32" alt="Claude Code" /><br /><sub>Claude Code</sub></td>
    <td align="center"><img src="docs/assets/logos/codex.svg" width="32" alt="Codex" /><br /><sub>Codex</sub></td>
    <td align="center"><img src="docs/assets/logos/cursor.svg" width="32" alt="Cursor" /><br /><sub>Cursor</sub></td>
    <td align="center"><img src="docs/assets/logos/bash.svg" width="32" alt="Bash" /><br /><sub>Bash</sub></td>
    <td align="center"><img src="docs/assets/logos/http.svg" width="32" alt="HTTP" /><br /><sub>HTTP</sub></td>
  </tr>
</table>
</div>

<p align="center">
  <a href="https://www.star-history.com/?repos=JungHoonGhae%2Fsmartstore-cli&type=date&legend=top-left">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=JungHoonGhae/smartstore-cli&type=date&theme=dark&legend=top-left" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=JungHoonGhae/smartstore-cli&type=date&legend=top-left" />
      <img alt="Star History Chart" src="https://api.star-history.com/image?repos=JungHoonGhae/smartstore-cli&type=date&legend=top-left" width="600" />
    </picture>
  </a>
</p>

## Quick Start

### For Human

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/JungHoonGhae/smartstore-cli/main/install.sh | sh

# Auth helper 설치 (Python 3.10+)
pip install -e /usr/local/share/storectl/auth-helper
# playwright install chromium  ← 불필요 (시스템 Chrome 사용)

# 설치 확인
storectl version
storectl doctor
storectl auth login
storectl seller info --output json
```

### From Source

```bash
git clone https://github.com/JungHoonGhae/smartstore-cli.git
cd smartstore-cli
make build
pip install -e auth-helper/
# playwright install chromium  ← 불필요 (시스템 Chrome 사용)
bin/storectl doctor
```

### For AI Agent

```bash
# storectl은 AI 에이전트가 직접 실행할 수 있습니다
storectl seller info --output json    # 구조화된 JSON 출력
storectl product list --output csv    # CSV로 파이프 가능
storectl stats daily --output json    # 매출 데이터 자동 수집
```

## 지원 범위

### 조회 (Read-Only)

| Command | Description | Output |
|---------|-------------|--------|
| `storectl seller info` | 스토어 정보 (스토어명, URL, 대표자, 연락처, 정산계좌) | table/json/csv |
| `storectl seller grade` | 판매자 등급 + 페널티 점수 | table/json/csv |
| `storectl product list` | 상품 목록 (`--page`, `--size` 페이지네이션) | table/json/csv |
| `storectl product show <id>` | 상품 상세 (채널상품번호로 조회) | table/json |
| `storectl product dashboard` | 상품 현황 카운트 (판매중/품절/수정요청) | table/json/csv |
| `storectl order list` | 주문/배송 대시보드 (상태별 건수) | table/json/csv |
| `storectl order list --detail` | 주문 목록 상세 (GraphQL, `--page`, `--size`) | table/json/csv |
| `storectl stats daily` | 매출 통계 (일간/주간/월간 PV, 주문수, 결제금액) | table/json/csv |
| `storectl settlement list` | 정산 대시보드 (오늘정산, 예정정산, 충전잔액) | table/json/csv |
| `storectl inquiry list` | 고객 문의 (상품문의/고객문의/톡톡) | table/json/csv |
| `storectl review list` | 리뷰 목록 (`--page`, `--size` 페이지네이션) | table/json/csv |
| `storectl review dashboard` | 리뷰 대시보드 (총 리뷰수, 평균점수) | table/json/csv |
| `storectl notification list` | 알림 목록 (`--count N` 최근 활동) | table/json/csv |

### 시스템

| Command | Description |
|---------|-------------|
| `storectl version` | 버전 정보 |
| `storectl doctor` | 시스템 건강 체크 (Python, Playwright, Chromium) |
| `storectl config init\|show` | 설정 파일 관리 |
| `storectl auth login` | 브라우저 기반 네이버 로그인 |
| `storectl auth status` | 세션 상태 (Last Used At 포함) |
| `storectl auth refresh` | Headless 세션 갱신 |
| `storectl auth logout` | 세션 삭제 |
| `storectl auth doctor` | 인증 요구사항 점검 |

## How It Works

```
User → storectl auth login
         ↓
       Python Playwright → Opens Chromium browser
         ↓
       User completes Naver ID login → Seller center
         ↓
       Captures cookies (NID_AUT, NID_SES, kit.session, NSI, ...)
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

- 세션은 `session.json`에 저장되며 API 호출마다 **자동으로 쿠키를 갱신**합니다
- 세션 만료 시 자동으로 `change-channel` + `login/init` 플로우를 시도합니다
- 자동 갱신 실패 시 `storectl auth login`으로 재로그인이 필요합니다
- `storectl auth status`에서 마지막 사용 시각과 세션 상태를 확인할 수 있습니다

### API Architecture

네이버 스마트스토어 판매자센터는 AngularJS SPA로 구성되어 있으며, 내부적으로 다음 API를 사용합니다:

| API Pattern | Method | Usage |
|-------------|--------|-------|
| `/api/v1/sellers/dashboards/*` | GET | 대시보드 데이터 (주문, 상품, 정산, 리뷰 등) |
| `/api/products/list/search` | POST | 상품 검색 |
| `/api/v3/contents/reviews/search` | POST | 리뷰 검색 |
| `/api/channels?_action=selectedChannel` | GET | 판매자/채널 정보 |
| `/o/v3/graphql` | POST | 주문 상세 (별도 SPA, Apollo Client) |
| `/api/login/change-channel` | POST | 세션 초기화 |

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
# playwright install chromium  ← 불필요 (시스템 Chrome 사용)
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

## 문서

### Reverse Engineering

API 엔드포인트는 브라우저 트래픽 캡처를 통해 리버스 엔지니어링되었습니다:

- [`docs/reverse-engineering/capture-guide.md`](docs/reverse-engineering/capture-guide.md) — Chrome DevTools 캡처 가이드
- [`docs/reverse-engineering/mitmproxy-guide.md`](docs/reverse-engineering/mitmproxy-guide.md) — mitmproxy 고급 가이드
- [`docs/api/CHANGELOG.md`](docs/api/CHANGELOG.md) — API 변경 이력

### Local Storage

| File | Purpose |
|------|---------|
| `<config-dir>/config.json` | 설정 파일 |
| `<config-dir>/session.json` | 브라우저 세션 (쿠키, 헤더, localStorage) |

Config directory: `~/Library/Application Support/storectl/` (macOS) or `~/.config/storectl/` (Linux)

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 JungHoon Ghae
