## ADDED Requirements

### Requirement: 판매자 정보 조회
`storectl seller info` 커맨드가 판매자 채널 정보(스토어명, URL, 연락처, 사업자 유형, 정산 계좌)를 표시해야 한다(SHALL).

#### Scenario: 판매자 정보 조회
- **WHEN** `storectl seller info`를 실행하면
- **THEN** 스토어명, 스토어 URL, 대표자명, 연락처, 사업자 유형, 은행/계좌 정보를 테이블 형식으로 표시해야 한다

### Requirement: 판매자 등급 조회
`storectl seller grade` 커맨드가 판매자 등급과 서비스 점수를 표시해야 한다(SHALL).

#### Scenario: 판매자 등급 표시
- **WHEN** `storectl seller grade`를 실행하면
- **THEN** 판매자 등급(actionGrade), 우수 서비스 여부, 페널티 점수를 표시해야 한다

### Requirement: 알림 목록 조회
`storectl notification list` 커맨드가 최근 알림 목록을 표시해야 한다(SHALL).

#### Scenario: 알림 목록 표시
- **WHEN** `storectl notification list`를 실행하면
- **THEN** 카테고리별 미읽은 알림 수와 최근 알림 항목을 표시해야 한다
