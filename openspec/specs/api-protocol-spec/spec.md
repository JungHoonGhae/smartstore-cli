## ADDED Requirements

### Requirement: API 엔드포인트 맵 문서화
시스템은 네이버 스마트스토어 판매자센터 웹 API의 모든 엔드포인트를 `docs/api/` 디렉토리에 도메인별 Markdown 파일로 문서화해야 한다(SHALL). 각 엔드포인트 문서는 HTTP 메서드, URL 경로, 필수/선택 쿼리 파라미터, 요청 헤더, 응답 JSON 구조를 포함해야 한다(MUST).

#### Scenario: 상품 API 엔드포인트 문서 존재
- **WHEN** 개발자가 `docs/api/products.md` 파일을 열면
- **THEN** 상품 목록 조회와 상품 상세 조회에 대한 실제 엔드포인트 URL, HTTP 메서드, 쿼리 파라미터, 응답 JSON 예시가 포함되어 있어야 한다

#### Scenario: 모든 도메인 커버리지
- **WHEN** `docs/api/` 디렉토리를 조회하면
- **THEN** products, orders, stats, settlements, inquiries, reviews 각 도메인에 대한 문서 파일이 존재해야 한다

### Requirement: 인증 프로토콜 문서화
시스템은 판매자센터 API 인증에 필요한 쿠키, 헤더, 토큰의 전체 목록과 획득 방법을 문서화해야 한다(SHALL). NID_AUT, NID_SES 외에 추가로 필요한 인증 요소(CSRF 토큰, 세션 ID, API 키 등)가 있다면 모두 식별해야 한다(MUST).

#### Scenario: 인증 요소 식별
- **WHEN** 브라우저 로그인 후 판매자센터 API 요청 트래픽을 캡처하면
- **THEN** 요청 헤더에서 인증에 필요한 모든 쿠키와 커스텀 헤더를 식별하고 `docs/api/authentication.md`에 문서화해야 한다

#### Scenario: 세션 만료 패턴
- **WHEN** 세션이 만료된 쿠키로 API를 호출하면
- **THEN** 반환되는 HTTP 상태 코드와 응답 본문 패턴을 문서화하여 클라이언트가 세션 만료를 정확히 감지할 수 있어야 한다

### Requirement: API 응답 스키마 정의
시스템은 각 API 엔드포인트의 응답 JSON 구조를 JSON Schema 또는 Go struct 어노테이션으로 정의해야 한다(SHALL). 필수 필드와 선택 필드를 구분하고, 필드 타입과 가능한 enum 값을 명시해야 한다(MUST).

#### Scenario: 상품 목록 응답 스키마
- **WHEN** 상품 목록 API를 호출하면
- **THEN** 응답 JSON의 루트 구조(배열/객체 래핑), 페이지네이션 메타데이터, 각 상품 객체의 필드 타입이 문서에 정의된 스키마와 일치해야 한다

#### Scenario: 에러 응답 스키마
- **WHEN** 잘못된 파라미터로 API를 호출하면
- **THEN** 에러 응답의 JSON 구조(에러 코드, 메시지 필드)가 문서화되어 있어야 한다

### Requirement: 페이지네이션 프로토콜 문서화
시스템은 목록 API 엔드포인트의 페이지네이션 방식(offset/cursor/page 기반)을 식별하고 문서화해야 한다(SHALL). 페이지 크기 파라미터, 다음 페이지 요청 방법, 총 개수 필드를 명시해야 한다(MUST).

#### Scenario: 주문 목록 페이지네이션
- **WHEN** 주문이 100건 이상인 판매자가 주문 목록 API를 호출하면
- **THEN** 첫 페이지 응답에서 다음 페이지를 요청할 수 있는 파라미터 정보를 추출할 수 있어야 한다

### Requirement: API Rate Limiting 정책 문서화
시스템은 판매자센터 API의 rate limiting 응답 패턴을 식별하고 문서화해야 한다(SHALL). 429 응답 코드, Retry-After 헤더, 또는 커스텀 제한 응답이 있다면 기록해야 한다(MUST).

#### Scenario: 연속 API 호출 시 제한 감지
- **WHEN** 동일 엔드포인트를 짧은 간격으로 반복 호출하면
- **THEN** rate limiting 응답의 HTTP 상태 코드와 응답 본문 패턴이 문서화되어 있어야 한다
