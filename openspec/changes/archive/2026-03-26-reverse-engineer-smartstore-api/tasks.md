## 1. 트래픽 캡처 및 분석 환경 구축

- [x] 1.1 `docs/reverse-engineering/capture-guide.md` 작성 — Chrome DevTools로 판매자센터 API 트래픽 캡처하는 단계별 가이드
- [x] 1.2 `docs/reverse-engineering/mitmproxy-guide.md` 작성 — mitmproxy 기반 고급 캡처 가이드 (CA 설치, 필터 스크립트)
- [x] 1.3 `scripts/analyze-har.py` HAR 파일 분석 스크립트 작성 — 엔드포인트 목록 추출, 호출 빈도, 응답 스키마 추론

## 2. API 프로토콜 캡처 및 문서화

- [x] 2.1 판매자센터 로그인 후 인증 관련 쿠키/헤더 전수 캡처 및 `docs/api/authentication.md` 작성
- [x] 2.2 상품 관리 페이지 API 트래픽 캡처 및 `docs/api/products.md` 엔드포인트 사양 작성
- [x] 2.3 주문 관리 페이지 API 트래픽 캡처 및 `docs/api/orders.md` 엔드포인트 사양 작성
- [x] 2.4 통계/매출 페이지 API 트래픽 캡처 및 `docs/api/stats.md` 엔드포인트 사양 작성
- [x] 2.5 정산 페이지 API 트래픽 캡처 및 `docs/api/settlements.md` 엔드포인트 사양 작성
- [x] 2.6 고객문의 페이지 API 트래픽 캡처 및 `docs/api/inquiries.md` 엔드포인트 사양 작성
- [x] 2.7 리뷰 페이지 API 트래픽 캡처 및 `docs/api/reviews.md` 엔드포인트 사양 작성
- [x] 2.8 페이지네이션 방식 확인 및 `docs/api/pagination.md` 문서화

## 3. 데이터 모델 재설계

- [x] 3.1 실제 API 응답 기반으로 `internal/domain/models.go`의 `Product` struct 재설계
- [x] 3.2 실제 API 응답 기반으로 `Order` struct 재설계
- [x] 3.3 실제 API 응답 기반으로 `DailyStats`, `MonthlyStats` struct 재설계
- [x] 3.4 실제 API 응답 기반으로 `Settlement` struct 재설계
- [x] 3.5 실제 API 응답 기반으로 `Inquiry` struct 재설계
- [x] 3.6 실제 API 응답 기반으로 `Review` struct 재설계

## 4. API 클라이언트 핵심 인프라

- [x] 4.1 `internal/client/client.go` — 공통 요청 빌더 구현 (인증 헤더, CSRF 토큰, Referer 자동 설정)
- [x] 4.2 `internal/client/client.go` — rate limiter 구현 (요청 간 최소 200ms 간격, 429 응답 시 재시도)
- [x] 4.3 `internal/client/client.go` — 페이지네이션 핸들러 구현 (전체 수집 + 페이지 단위 조회)
- [x] 4.4 `internal/client/errors.go` — 에러 타입 강화 (`ErrSessionExpired`, `ErrRateLimited` 추가)
- [x] 4.5 `internal/client/client.go` — 세션 검증 엔드포인트를 실제 API로 교체

## 5. 도메인별 API 클라이언트 구현

- [x] 5.1 `internal/client/product.go` — 실제 상품 API 엔드포인트로 교체 및 응답 파싱 구현
- [x] 5.2 `internal/client/order.go` — 실제 주문 API 엔드포인트로 교체 및 상태 필터 구현
- [x] 5.3 `internal/client/stats.go` — 실제 통계 API 엔드포인트로 교체 (일별/월별)
- [x] 5.4 `internal/client/settlement.go` — 실제 정산 API 엔드포인트로 교체
- [x] 5.5 `internal/client/inquiry.go` — 실제 고객문의 API 엔드포인트로 교체
- [x] 5.6 `internal/client/review.go` — 실제 리뷰 API 엔드포인트로 교체

## 6. 세션 관리 보강

- [x] 6.1 `internal/session/store.go` — 추가 인증 요소(CSRF 토큰 등) 저장 지원
- [x] 6.2 `internal/auth/playwright.go` — Playwright storage state에서 추가 인증 요소 추출 로직

## 7. 출력 포맷터 업데이트

- [x] 7.1 `internal/output/product.go` — 변경된 Product 모델에 맞게 테이블/JSON/CSV 포맷터 수정
- [x] 7.2 `internal/output/order.go` — 변경된 Order 모델에 맞게 포맷터 수정
- [x] 7.3 `internal/output/stats.go` — 변경된 Stats 모델에 맞게 포맷터 수정
- [x] 7.4 `internal/output/settlement.go` — 변경된 Settlement 모델에 맞게 포맷터 수정
- [x] 7.5 `internal/output/inquiry.go` — 변경된 Inquiry 모델에 맞게 포맷터 수정
- [x] 7.6 `internal/output/review.go` — 변경된 Review 모델에 맞게 포맷터 수정

## 8. 테스트 및 검증

- [x] 8.1 실제 판매자 계정으로 `storectl product list` 동작 검증
- [x] 8.2 실제 판매자 계정으로 `storectl order list --status all` 동작 검증
- [x] 8.3 실제 판매자 계정으로 `storectl stats daily` / `storectl stats monthly` 동작 검증
- [x] 8.4 실제 판매자 계정으로 `storectl settlement list` 동작 검증
- [x] 8.5 실제 판매자 계정으로 `storectl inquiry list` / `storectl review list` 동작 검증
- [x] 8.6 세션 만료 시 적절한 에러 메시지 출력 검증
- [x] 8.7 `docs/api/CHANGELOG.md` 생성 — API 변경 이력 추적 시작

## 9. 프로토콜 변경 감지 도구

- [x] 9.1 `scripts/diff-api.py` — 새 HAR 캡처와 기존 API 문서를 비교하여 변경 사항 감지하는 스크립트 작성
