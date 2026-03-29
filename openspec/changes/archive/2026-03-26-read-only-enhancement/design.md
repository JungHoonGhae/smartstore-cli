## Context

`storectl`이 실제 네이버 스마트스토어 API와 통신하지만, 현재 구현은 대시보드 집계 API만 사용한다. 캡처된 API fixture(`fixtures/responses/`)에서 추가 엔드포인트들의 응답 구조가 확인되었으며, 세션 초기화 플로우도 파악되었다.

캡처된 미구현 API:
- `GET /api/channels?_action=selectedChannel` → 판매자/채널 상세 정보 (66KB)
- `GET /api/v1/sellers/dashboards/seller-grade` → 판매자 등급
- `GET /api/seller/notification/user-activities?count=10` → 알림 목록
- `GET /api/v1/sellers/context/for-resource-menu` → 리소스 메뉴 (권한 정보)

주문 상세 조회는 별도 SPA(`/o/v3/`)에서 처리되므로 해당 SPA의 API를 추가 캡처해야 한다.

## Goals / Non-Goals

**Goals:**
- 판매자 정보/등급/알림 조회 커맨드 구현
- 상품/리뷰 목록 페이지네이션 (`--page`, `--size` 플래그)
- Go 클라이언트 세션 초기화 자동화
- 주문 목록 상세 조회 (browse로 캡처 필요)
- `storectl product show <id>` 실제 동작

**Non-Goals:**
- 쓰기 API (상품 등록/수정) — 별도 change
- 주문 상태 변경 — 쓰기 작업
- 실시간 알림 구독

## Decisions

### 1. 세션 초기화: 첫 API 호출 시 lazy init

**선택**: 첫 API 호출이 실패(GW.AUTHN)하면 change-channel + init을 자동 수행 후 재시도
**이유**: 대부분의 대시보드 API는 초기화 없이도 동작. 초기화가 필요한 엔드포인트에서만 수행하면 불필요한 HTTP 요청 절약.

### 2. 판매자 정보: channel-selected 엔드포인트 활용

**선택**: `GET /api/channels?_action=selectedChannel`에서 필요한 필드만 추출
**이유**: 이 엔드포인트가 가장 풍부한 판매자/채널 정보를 반환 (스토어명, URL, 연락처, 은행계좌 등)

### 3. 주문 상세: browse 캡처 후 구현

**선택**: `/o/v3/` SPA의 주문 API를 browse로 캡처하여 구현
**이유**: 주문 관리는 별도 SPA이므로 메인 SPA API와 다른 엔드포인트를 사용

### 4. 페이지네이션: 커맨드 플래그 방식

**선택**: `--page`(기본 1)와 `--size`(기본 10) 플래그를 목록 커맨드에 추가
**이유**: 간단하고 직관적. API가 이미 page/pageSize 파라미터를 지원.

## Risks / Trade-offs

- **[주문 API 캡처]** `/o/v3/` SPA 주문 API는 추가 browse 캡처가 필요 → 세션이 살아있을 때 수행해야 함
- **[세션 초기화 순환]** 초기화 API 자체가 실패하면 무한 재시도 위험 → 재시도 1회로 제한
