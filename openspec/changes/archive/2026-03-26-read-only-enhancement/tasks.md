## 1. 세션 초기화 자동화

- [x] 1.1 `internal/client/client.go` — `initSession` 메서드: `/api/login/channels` → `POST /api/login/change-channel` → `GET /api/login/init` 순차 호출
- [x] 1.2 `internal/client/client.go` — `getJSON`/`postJSON` AuthError 재시도 시 `initSession`도 시도
- [x] 1.3 `internal/domain/models.go` — `LoginChannel` struct 추가 (channelNo, roleNo, channelName)

## 2. 판매자 커맨드

- [x] 2.1 `internal/domain/models.go` — `SellerInfo` struct (스토어명, URL, 대표자명, 연락처, 사업자유형, 정산계좌)
- [x] 2.2 `internal/client/seller.go` — `GetSellerInfo` + `GetSellerGrade` + `GetPenalties`
- [x] 2.3 `internal/output/seller.go` — 판매자 정보/등급 테이블/JSON/CSV 포맷터
- [x] 2.4 `cmd/storectl/seller.go` — `storectl seller info` / `storectl seller grade` 커맨드
- [x] 2.5 `cmd/storectl/root.go` — seller 커맨드 등록

## 3. 알림 커맨드

- [x] 3.1 `internal/domain/models.go` — `NotificationCounts`, `NotificationActivity` struct
- [x] 3.2 `internal/client/notification.go` — `GetNotificationCounts` + `GetNotificationActivities`
- [x] 3.3 `internal/output/notification.go` — 알림 포맷터
- [x] 3.4 `cmd/storectl/notification.go` — `storectl notification list` 커맨드
- [x] 3.5 `cmd/storectl/root.go` — notification 커맨드 등록

## 4. 페이지네이션

- [x] 4.1 `cmd/storectl/product.go` — `--page`, `--size` 플래그 추가
- [x] 4.2 `internal/client/product.go` — `ListProducts`에 page, size 파라미터 추가
- [x] 4.3 `internal/domain/models.go` — `ProductSearchResponse`에 페이지네이션 메타 필드 추가 (pageable, total)
- [x] 4.4 `internal/output/product.go` — 페이지 정보 표시 추가
- [x] 4.5 `cmd/storectl/review.go` — `--page`, `--size` 플래그 추가
- [x] 4.6 `internal/client/review.go` — page/size CLI 연결

## 5. 상품 상세 조회

- [x] 5.1 상품 상세는 검색 API 기반으로 구현 (계정에 상품 없어 직접 엔드포인트 불가)
- [x] 5.2 `internal/client/product.go` — `GetProduct` 검색 API 기반 구현
- [x] 5.3 `internal/domain/models.go` — 기존 `ProductSearchItem` 재활용

## 6. 주문 상세 조회

- [x] 6.1 `/browse`로 주문 관리 SPA(`/o/v3/`) API 캡처 — GraphQL (`POST /o/v3/graphql`) 발견
- [x] 6.2 `internal/domain/models.go` — `OrderListResponse`, `OrderItem`, `OrderPagination` struct
- [x] 6.3 `internal/client/order.go` — `ListOrders` GraphQL 주문 목록 API 구현
- [x] 6.4 `internal/output/order.go` — `WriteOrderList` 주문 목록 포맷터
- [x] 6.5 `cmd/storectl/order.go` — 기본 대시보드 + `--detail` 플래그로 GraphQL 조회

## 7. 테스트 및 검증

- [x] 7.1 `storectl seller info` 동작 검증
- [x] 7.2 `storectl seller grade` 동작 검증
- [x] 7.3 `storectl notification list` 동작 검증
- [x] 7.4 `storectl product list --page 1 --size 5` 동작 검증
- [x] 7.5 `storectl review list --page 1 --size 5` 동작 검증
- [x] 7.6 세션 초기화 자동화 검증 (세션 만료 후 자동 복구)
