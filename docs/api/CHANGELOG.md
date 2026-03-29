# API Changelog

## 2026-03-26 — Initial Discovery

- Discovered actual API base pattern: `/api/v1/sellers/dashboards/*` for dashboard data
- Product search uses POST `/api/products/list/search`
- Reviews search uses POST `/api/v3/contents/reviews/search`
- Session validation via `/api/v1/sellers/auths/login/check-neoid-session`
- SPA uses AngularJS with hash-based routing
- Order management is separate SPA at `/o/v3/`
