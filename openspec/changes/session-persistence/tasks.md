## 1. 세션 모델 확장

- [x] 1.1 `internal/session/store.go` — `Session` struct에 `LastUsedAt` 필드 추가
- [x] 1.2 `internal/session/store.go` — Save 시 `LastUsedAt` 자동 갱신

## 2. 응답 쿠키 자동 갱신

- [x] 2.1 `internal/client/client.go` — 응답 Set-Cookie 자동 캡처 (`updateCookiesFromResponse`)
- [x] 2.2 `internal/client/client.go` — 성공 응답 후 변경된 쿠키를 session.json에 저장

## 3. 자동 재시도 (Retry-on-auth-failure)

- [x] 3.1 `internal/client/client.go` — `getJSON`/`postJSON`에서 AuthError 발생 시 세션 갱신 후 1회 재시도 로직
- [x] 3.2 `internal/client/client.go` — `SessionRefresher` 인터페이스 정의 및 Client에 주입

## 4. Headless 자동 재로그인

- [x] 4.1 `internal/auth/service.go` — `Refresh(ctx)` / `RefreshSession(ctx)` 메서드
- [ ] 4.2 `auth-helper/storectl_auth_helper/cli.py` — `refresh` 서브커맨드 (기존 storage state 로드 headless)
- [x] 4.3 `internal/auth/helper.go` — 기존 `Login` 메서드 재활용 (refresh = headless login)

## 5. CLI 커맨드

- [x] 5.1 `cmd/storectl/auth.go` — `storectl auth refresh` 커맨드 추가
- [x] 5.2 `cmd/storectl/auth.go` — `storectl auth status`에 마지막 사용 시각 표시
- [x] 5.3 `cmd/storectl/root.go` — Client 생성 시 SessionRefresher 연결

## 6. 테스트

- [x] 6.1 `storectl order list` 실행 → LastUsedAt 자동 갱신 확인
- [ ] 6.2 `storectl auth refresh` 실행 → 세션 갱신 확인
- [x] 6.3 `storectl auth status` — 마지막 사용 시각 표시 확인
