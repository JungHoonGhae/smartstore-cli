## Why

현재 `storectl` API 클라이언트가 `/api/products`, `/api/orders` 등 추정 기반 플레이스홀더 엔드포인트를 사용하고 있어 실제 네이버 스마트스토어 판매자센터와 통신할 수 없다. 네이버 스마트스토어는 공식 문서화된 seller center web API가 없으므로, 브라우저 DevTools와 프로토콜 리버스 엔지니어링 기법으로 실제 API를 분석하고 문서화하여 CLI가 실제로 동작하도록 해야 한다.

## What Changes

- 네이버 스마트스토어 판매자센터 웹 API 프로토콜 사양 문서 작성 (엔드포인트, 요청/응답 포맷, 인증 메커니즘)
- `internal/client/` 전체 리팩터링: 플레이스홀더 엔드포인트를 실제 API 엔드포인트로 교체
- **BREAKING**: API 응답 구조 변경에 따른 `internal/domain/models.go` 데이터 모델 전면 재설계
- 세션 관리 로직 보강: 실제 쿠키/토큰 기반 인증 플로우 반영
- API 요청 시 필요한 헤더, 쿼리 파라미터, CSRF 토큰 등 프로토콜 세부사항 구현
- 페이지네이션, 에러 응답 코드 등 실제 API 동작 패턴 문서화 및 구현

## Capabilities

### New Capabilities
- `api-protocol-spec`: 네이버 스마트스토어 판매자센터 웹 API 프로토콜 사양 (엔드포인트 맵, 인증 플로우, 요청/응답 스키마, 에러 코드)
- `traffic-capture-guide`: 브라우저 DevTools / mitmproxy를 활용한 API 트래픽 캡처 및 분석 절차 가이드
- `api-client-implementation`: 리버스 엔지니어링된 프로토콜 기반 Go HTTP 클라이언트 구현 사양

### Modified Capabilities

(기존 spec 없음)

## Impact

- **코드**: `internal/client/*.go` 전체, `internal/domain/models.go`, `internal/session/store.go`, `internal/auth/service.go`
- **API**: 모든 도메인 커맨드(product, order, stats, settlement, inquiry, review)의 실제 동작
- **의존성**: mitmproxy 또는 브라우저 DevTools (개발 시 캡처용, 런타임 불필요)
- **시스템**: 네이버 판매자센터 웹 프론트엔드의 API 호출 패턴에 의존 — API 변경 시 유지보수 필요
