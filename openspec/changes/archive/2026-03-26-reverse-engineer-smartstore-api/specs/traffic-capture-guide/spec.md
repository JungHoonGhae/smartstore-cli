## ADDED Requirements

### Requirement: DevTools 트래픽 캡처 가이드
시스템은 브라우저 DevTools를 사용하여 네이버 판매자센터 API 트래픽을 캡처하는 단계별 가이드를 `docs/reverse-engineering/capture-guide.md`에 제공해야 한다(SHALL). Chrome/Edge DevTools Network 탭 사용법, XHR/Fetch 필터링, HAR 파일 내보내기 절차를 포함해야 한다(MUST).

#### Scenario: 개발자가 상품 API 트래픽 캡처
- **WHEN** 가이드를 따라 판매자센터에 로그인하고 상품 관리 페이지를 방문하면
- **THEN** DevTools Network 탭에서 상품 관련 API 요청을 식별하고 HAR 파일로 내보낼 수 있어야 한다

#### Scenario: 캡처 필터 설정
- **WHEN** DevTools Network 탭에서 API 요청만 필터링하려고 하면
- **THEN** 가이드에 제공된 필터 패턴(XHR/Fetch, URL 패턴)으로 판매자센터 API 요청만 분리할 수 있어야 한다

### Requirement: mitmproxy 고급 캡처 가이드
시스템은 mitmproxy를 사용한 고급 트래픽 캡처 방법을 `docs/reverse-engineering/mitmproxy-guide.md`에 문서화해야 한다(SHALL). CA 인증서 설치, 프록시 설정, 필터 스크립트 작성, 캡처 데이터 내보내기를 포함해야 한다(MUST).

#### Scenario: mitmproxy로 전체 세션 캡처
- **WHEN** 가이드를 따라 mitmproxy를 설정하고 브라우저를 프록시에 연결하면
- **THEN** 판매자센터 접속부터 로그아웃까지 모든 API 트래픽을 캡처하고 재생할 수 있어야 한다

### Requirement: HAR 파일 분석 도구/스크립트
시스템은 캡처된 HAR 파일에서 API 엔드포인트를 자동 추출하고 요약하는 분석 스크립트를 `tools/` 또는 `scripts/` 디렉토리에 제공해야 한다(SHALL).

#### Scenario: HAR 파일에서 엔드포인트 목록 추출
- **WHEN** 캡처된 HAR 파일을 분석 스크립트에 입력하면
- **THEN** 고유 API 엔드포인트 목록, 각 엔드포인트의 호출 횟수, HTTP 메서드, 응답 상태 코드 요약이 출력되어야 한다

#### Scenario: 응답 스키마 자동 추론
- **WHEN** 동일 엔드포인트에 대한 여러 응답이 HAR 파일에 포함되어 있으면
- **THEN** 분석 스크립트가 공통 필드 구조와 타입을 추론하여 JSON Schema 초안을 생성할 수 있어야 한다

### Requirement: 프로토콜 변경 감지 절차
시스템은 기존 문서화된 API 사양과 현재 실제 API 동작을 비교하여 변경 사항을 감지하는 절차를 문서화해야 한다(SHALL).

#### Scenario: API 응답 구조 변경 감지
- **WHEN** 새로운 HAR 파일을 캡처하여 기존 문서와 비교하면
- **THEN** 추가/제거/변경된 필드 또는 엔드포인트를 식별할 수 있어야 한다
