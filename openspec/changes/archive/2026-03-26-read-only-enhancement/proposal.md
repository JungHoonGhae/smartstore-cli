## Why

`storectl` CLI가 실제 네이버 스마트스토어 API에 연결되어 동작하지만, 현재 각 커맨드가 대시보드 요약 데이터만 반환한다. 실제 판매자가 필요로 하는 상세 데이터(주문 목록, 판매자 정보, 판매자 등급, 알림)와 페이지네이션 기능이 없어 실용성이 부족하다. 또한 Go 클라이언트가 세션 초기화 플로우(change-channel + init)를 자동 수행하지 않아 일부 API 호출이 실패할 수 있다.

## What Changes

- `storectl seller info` / `storectl seller grade` 커맨드 추가
- `storectl notification list` 커맨드 추가
- `storectl product list` / `storectl review list`에 `--page`, `--size` 페이지네이션 플래그 추가
- 주문 목록 실제 조회 API 캡처 및 `storectl order list` 확장 (v3 SPA API)
- Go 클라이언트에 세션 초기화 플로우 (change-channel + login/init) 자동화
- `storectl product show <id>` 실제 API 연결

## Capabilities

### New Capabilities
- `seller-commands`: 판매자 정보, 등급, 알림 조회 커맨드
- `pagination`: 상품/리뷰 목록에 페이지네이션 지원
- `session-init`: Go 클라이언트 세션 초기화 자동화 (change-channel + init)
- `order-detail`: 주문 목록 상세 조회 (대시보드 카운트가 아닌 실제 주문 데이터)

### Modified Capabilities

(없음)

## Impact

- **코드**: `cmd/storectl/` 새 커맨드 파일, `internal/client/` 새 API 메서드, `internal/domain/models.go` 모델 추가, `internal/output/` 포맷터 추가
- **CLI**: 새 서브커맨드 4개 + 기존 커맨드 플래그 확장
- **세션**: 첫 API 호출 시 자동 세션 초기화로 안정성 향상
