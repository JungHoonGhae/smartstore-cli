## Context

현재 `storectl`은 Playwright로 로그인한 세션을 `session.json`에 저장하고 API 호출 시 쿠키를 첨부한다. 세션이 서버 측에서 만료되면 403/401 에러가 발생하고 사용자가 수동으로 다시 로그인해야 한다.

네이버 스마트스토어 세션 특성:
- NID 쿠키 (NID_AUT, NID_SES): 네이버 전체 로그인 — 장기 유효 (브라우저 세션 기반)
- kit.session: 커머스 플랫폼 세션 — ~30분 비활성 후 만료
- NSI: 스마트스토어 세션 — change-channel 후 설정

## Goals / Non-Goals

**Goals:**
- API 호출 실패(401/403) 시 자동으로 세션 갱신 시도 후 재호출
- 세션 마지막 사용 시각 기록으로 만료 예측
- `storectl auth refresh` 커맨드로 수동 세션 갱신
- 응답의 `Set-Cookie` 헤더로 쿠키 자동 업데이트

**Non-Goals:**
- 완전한 무인 운영 (2FA/CAPTCHA 필요 시 여전히 수동 로그인)
- NID 쿠키 자체의 갱신 (이건 네이버 로그인 수준이라 Playwright 필요)
- 백그라운드 데몬으로 세션 유지

## Decisions

### 1. 세션 갱신 전략: Retry-on-failure

**선택**: API 호출이 AuthError를 반환하면 한 번 세션 갱신 시도 후 재호출
**대안**: 매 호출 전 사전 검증
**이유**: 사전 검증은 매번 추가 HTTP 요청이 필요. Retry-on-failure는 실패할 때만 갱신 시도하므로 효율적.

### 2. 쿠키 갱신: 응답 Set-Cookie 캡처

**선택**: HTTP 응답의 Set-Cookie 헤더를 파싱하여 session.json 업데이트
**이유**: 네이버 서버가 NSI 등 쿠키를 갱신할 때 자동 반영. Go의 `http.Client`에 CookieJar를 사용하면 자동 관리 가능.

### 3. 자동 재로그인: Headless Playwright

**선택**: 세션 만료 시 기존 NID 쿠키를 심은 Playwright 컨텍스트로 판매자센터 접속 → 자동 채널 선택
**이유**: NID 쿠키가 아직 유효하면 브라우저 상호작용 없이 세션 갱신 가능. 실패하면 사용자에게 수동 로그인 안내.

## Risks / Trade-offs

- **[NID 만료]** NID 쿠키도 만료되면 headless 재로그인 불가 → 수동 `auth login` 필요. 에러 메시지로 안내.
- **[Race condition]** 여러 CLI 호출이 동시에 세션 갱신 시도 → 파일 잠금으로 방지.
- **[쿠키 동기화]** Set-Cookie 갱신 시 session.json 쓰기 빈도 → 성공 응답에서만 갱신.
