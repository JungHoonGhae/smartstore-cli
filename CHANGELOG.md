# Changelog

## [0.1.0] - 2026-03-26

Initial release of smartstore-cli (`storectl`).

### Added
- Browser-assisted login via Playwright (Naver ID → seller center session capture)
- Real API integration via reverse-engineered seller center endpoints
- **Seller commands**: `storectl seller info`, `storectl seller grade`
- **Product commands**: `storectl product list` (paginated), `storectl product show <id>`, `storectl product dashboard`
- **Order commands**: `storectl order list` (dashboard), `storectl order list --detail` (GraphQL)
- **Stats**: `storectl stats daily` (daily/weekly/monthly PV, orders, pay amount)
- **Settlement**: `storectl settlement list` (today/expected/charge balance)
- **Inquiry**: `storectl inquiry list` (product/customer/talktalk counts)
- **Review**: `storectl review list` (paginated), `storectl review dashboard`
- **Notification**: `storectl notification list` (category counts + recent activities)
- **Auth**: login, status (with Last Used At), refresh (headless), logout, doctor
- **Session management**: auto cookie refresh, auto session init (change-channel + login/init), rate limiter (200ms)
- **Output formats**: table, JSON, CSV for all data commands
- **System**: version, doctor, config init/show
- **Docs**: capture guide, mitmproxy guide, API changelog
- **CI/CD**: GitHub Actions for CI (test + build) and Release (5 platforms)

### Note
- 현재 버전은 **읽기 전용(read-only)** 입니다
- 안정화 후 상품 등록/수정 등 쓰기 기능 확장 예정
