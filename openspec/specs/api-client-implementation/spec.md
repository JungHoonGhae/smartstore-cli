## ADDED Requirements

### Requirement: 실제 엔드포인트 기반 API 클라이언트
`internal/client/` 패키지는 리버스 엔지니어링으로 식별된 실제 네이버 판매자센터 API 엔드포인트를 사용해야 한다(SHALL). 플레이스홀더 경로(`/api/products` 등)를 실제 엔드포인트로 교체해야 한다(MUST).

#### Scenario: 상품 목록 조회
- **WHEN** `client.ListProducts(ctx)`를 호출하면
- **THEN** 실제 판매자센터 상품 목록 API 엔드포인트로 HTTP 요청을 보내고 상품 목록을 반환해야 한다

#### Scenario: 주문 상태별 조회
- **WHEN** `client.ListOrders(ctx, "pending")`를 호출하면
- **THEN** 실제 판매자센터 주문 API에 적절한 상태 필터 파라미터를 포함하여 요청하고 해당 상태의 주문 목록을 반환해야 한다

### Requirement: 실제 API 응답 기반 데이터 모델
`internal/domain/models.go`의 데이터 모델은 실제 API 응답의 JSON 구조에 맞게 재설계되어야 한다(SHALL). JSON 필드 태그는 실제 API 응답의 키 이름과 일치해야 한다(MUST). 선택적 필드는 포인터 또는 `omitempty` 태그를 사용해야 한다(MUST).

#### Scenario: Product 모델 매핑
- **WHEN** 실제 상품 API 응답 JSON을 `domain.Product` struct로 언마샬하면
- **THEN** 상품명, 가격, 재고, 상태 등 CLI 표시에 필요한 필드가 정확히 매핑되어야 한다

#### Scenario: 알 수 없는 필드 무시
- **WHEN** API 응답에 Go struct에 정의되지 않은 필드가 포함되어 있으면
- **THEN** `json.Decoder`가 해당 필드를 무시하고 에러 없이 디코딩되어야 한다

### Requirement: 공통 요청 빌더
`internal/client/client.go`는 모든 API 요청에 공통으로 필요한 헤더, 쿠키, 쿼리 파라미터를 자동으로 설정하는 요청 빌더를 제공해야 한다(SHALL). 인증 토큰, CSRF 토큰, User-Agent, Referer 등을 포함해야 한다(MUST).

#### Scenario: 인증 헤더 자동 설정
- **WHEN** API 요청을 빌드하면
- **THEN** 세션에서 로드된 모든 인증 쿠키와 필수 헤더가 요청에 포함되어야 한다

#### Scenario: CSRF 토큰이 필요한 경우
- **WHEN** API가 CSRF 토큰을 요구하는 경우
- **THEN** 세션 또는 초기 페이지 로드에서 CSRF 토큰을 추출하여 요청 헤더에 포함해야 한다

### Requirement: 페이지네이션 핸들러
목록 API 호출 시 페이지네이션을 자동으로 처리하는 헬퍼를 제공해야 한다(SHALL). 호출자는 전체 결과를 한 번에 받거나 페이지 단위로 이터레이션할 수 있어야 한다(MUST).

#### Scenario: 전체 상품 목록 자동 수집
- **WHEN** `client.ListProducts(ctx)`를 호출하고 상품이 여러 페이지에 걸쳐 있으면
- **THEN** 클라이언트가 자동으로 모든 페이지를 순회하여 전체 상품 목록을 반환해야 한다

#### Scenario: 페이지 단위 조회
- **WHEN** 호출자가 특정 페이지만 요청하면
- **THEN** 해당 페이지의 결과만 반환하고 페이지네이션 메타데이터(총 개수, 현재 페이지, 다음 페이지 존재 여부)를 함께 반환해야 한다

### Requirement: 에러 처리 강화
API 클라이언트는 실제 API의 에러 응답 패턴에 맞게 에러 타입을 정의하고 처리해야 한다(SHALL). 세션 만료, 권한 없음, rate limiting, 서버 에러를 구분해야 한다(MUST).

#### Scenario: 세션 만료 감지
- **WHEN** API 응답이 세션 만료를 나타내면
- **THEN** `ErrSessionExpired` 에러를 반환하고 CLI가 `storectl auth login` 재실행을 안내해야 한다

#### Scenario: Rate limiting 대응
- **WHEN** API 응답이 rate limiting을 나타내면
- **THEN** `ErrRateLimited` 에러를 반환하고 Retry-After 정보가 있다면 포함해야 한다

### Requirement: Rate Limiting 구현
API 클라이언트는 판매자센터 서버에 과도한 부하를 주지 않도록 요청 간 간격을 조절하는 rate limiter를 내장해야 한다(SHALL).

#### Scenario: 연속 API 호출 시 간격 유지
- **WHEN** 여러 API 호출을 연속으로 실행하면
- **THEN** 요청 사이에 최소 간격(기본 200ms)을 유지해야 한다

#### Scenario: Rate limiting 응답 후 재시도
- **WHEN** API가 rate limiting 응답을 반환하면
- **THEN** 지정된 대기 시간 후 자동으로 재시도하고 최대 재시도 횟수를 초과하면 에러를 반환해야 한다
