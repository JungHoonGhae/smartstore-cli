## Why

`storectl` CLI가 네이버 스마트스토어 API를 성공적으로 호출하지만, 세션이 서버 측에서 ~30분 비활성 후 만료되면 수동으로 `storectl auth login`을 다시 실행해야 한다. CLI 사용성을 위해 세션 자동 갱신과 만료 감지 후 자동 재인증이 필요하다.

## What Changes

- API 호출 전 세션 유효성 사전 검증 및 만료 시 자동 재인증 시도
- 세션 갱신 메커니즘: API 호출 시 서버가 반환하는 `Set-Cookie` 헤더로 쿠키 자동 갱신
- 세션 만료 시간 추적: 마지막 성공 API 호출 시각 기록, TTL 기반 만료 예측
- Headless 자동 재로그인: 세션 만료 시 Playwright를 headless로 자동 실행하여 재인증 (기존 쿠키 기반)
- `storectl auth refresh` 커맨드 추가: 수동 세션 갱신

## Capabilities

### New Capabilities
- `session-refresh`: 세션 자동 갱신 및 TTL 기반 만료 관리 (쿠키 갱신, 만료 예측, 자동 재인증)

### Modified Capabilities

(없음)

## Impact

- **코드**: `internal/client/client.go`, `internal/session/store.go`, `internal/auth/service.go`, `cmd/storectl/auth.go`
- **동작**: API 호출 실패 시 자동 재시도 → 사용자 경험 개선
- **의존성**: Playwright headless 재로그인은 기존 NID 쿠키가 유효할 때만 동작
