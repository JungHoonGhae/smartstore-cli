## ADDED Requirements

### Requirement: 자동 세션 초기화
Go 클라이언트가 API 호출 실패 시 자동으로 change-channel + login/init 플로우를 수행해야 한다(SHALL).

#### Scenario: 첫 호출 시 세션 초기화
- **WHEN** API 호출이 GW.AUTHN 에러를 반환하면
- **THEN** 클라이언트가 change-channel과 login/init를 순차 호출한 후 원래 요청을 재시도해야 한다

#### Scenario: 초기화 실패 시 에러 전파
- **WHEN** 세션 초기화 자체가 실패하면
- **THEN** 원래 에러를 그대로 반환하고 무한 재시도를 방지해야 한다

### Requirement: 채널 정보 자동 탐색
세션 초기화 시 channelNo와 roleNo를 login/channels API에서 자동 획득해야 한다(SHALL).

#### Scenario: 채널 자동 선택
- **WHEN** 세션 초기화가 시작되면
- **THEN** `/api/login/channels`에서 첫 번째 채널의 channelNo와 roleNo를 획득하여 change-channel에 사용해야 한다
