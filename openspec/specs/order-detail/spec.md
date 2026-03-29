## ADDED Requirements

### Requirement: 주문 목록 상세 조회
`storectl order list`가 대시보드 카운트뿐 아니라 실제 주문 목록을 조회할 수 있어야 한다(SHALL). 주문 API를 browse로 캡처하여 구현한다.

#### Scenario: 주문 목록 조회
- **WHEN** `storectl order list`를 실행하면
- **THEN** 최근 주문 목록(주문번호, 상품명, 수량, 금액, 상태, 주문일)을 표시해야 한다

#### Scenario: 주문 대시보드 폴백
- **WHEN** 주문 목록 API가 사용 불가능하면
- **THEN** 기존 대시보드 카운트를 표시하고 사용자에게 안내해야 한다

### Requirement: 상품 상세 조회
`storectl product show <id>`가 실제 API로 단일 상품 정보를 반환해야 한다(SHALL).

#### Scenario: 상품 번호로 조회
- **WHEN** `storectl product show 12345`를 실행하면
- **THEN** 해당 상품의 상세 정보(상품명, 가격, 재고, 카테고리, 상태, 등록일)를 표시해야 한다
