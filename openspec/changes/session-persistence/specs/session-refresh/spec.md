## ADDED Requirements

### Requirement: API 호출 실패 시 자동 세션 갱신 및 재시도
API 호출이 AuthError(401/403/GW.AUTHN)를 반환하면 세션 갱신을 한 번 시도한 후 원래 요청을 재실행해야 한다(SHALL). 재시도도 실패하면 원래 에러를 반환해야 한다(MUST).

#### Scenario: 세션 만료 후 자동 복구
- **WHEN** API 호출이 403 GW.AUTHN 에러를 반환하면
- **THEN** 클라이언트가 자동으로 세션 갱신을 시도하고, 성공하면 원래 요청을 재실행하여 결과를 반환해야 한다

#### Scenario: 갱신 실패 시 에러 전파
- **WHEN** 세션 갱신도 실패하면
- **THEN** `ErrSessionExpired` 에러와 함께 `storectl auth login` 실행 안내를 반환해야 한다

### Requirement: 응답 쿠키 자동 갱신
HTTP 응답의 Set-Cookie 헤더에 새 쿠키가 포함되면 session.json에 자동으로 반영해야 한다(SHALL).

#### Scenario: NSI 쿠키 갱신
- **WHEN** API 응답이 새 NSI 쿠키를 Set-Cookie로 반환하면
- **THEN** session.json의 해당 쿠키 값이 업데이트되어야 한다

### Requirement: 세션 마지막 사용 시각 추적
세션의 마지막 성공 API 호출 시각을 기록하여 만료 예측에 사용해야 한다(SHALL).

#### Scenario: 마지막 사용 시각 업데이트
- **WHEN** API 호출이 성공(2xx)하면
- **THEN** session.json의 `last_used_at` 필드가 현재 시각으로 업데이트되어야 한다

#### Scenario: auth status에서 만료 예측 표시
- **WHEN** `storectl auth status`를 실행하면
- **THEN** 마지막 사용 시각과 예상 만료 시각을 표시해야 한다

### Requirement: Headless 자동 재로그인
세션 만료 시 기존 NID 쿠키가 유효하면 headless Playwright로 자동 재인증을 시도해야 한다(SHALL).

#### Scenario: NID 쿠키 유효 시 자동 재인증
- **WHEN** kit.session이 만료되었지만 NID_AUT/NID_SES가 유효하면
- **THEN** headless Playwright로 판매자센터 접속 → 새 세션 쿠키 획득 → session.json 업데이트

#### Scenario: NID 쿠키도 만료 시 사용자 안내
- **WHEN** NID 쿠키도 만료되어 headless 재인증이 실패하면
- **THEN** `storectl auth login` 수동 실행을 안내하는 에러 메시지 반환

### Requirement: auth refresh 커맨드
`storectl auth refresh` 커맨드로 수동 세션 갱신이 가능해야 한다(SHALL).

#### Scenario: 수동 세션 갱신
- **WHEN** `storectl auth refresh`를 실행하면
- **THEN** headless Playwright로 세션 갱신을 시도하고 결과를 표시해야 한다
