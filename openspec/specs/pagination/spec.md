## ADDED Requirements

### Requirement: 상품 목록 페이지네이션
`storectl product list`에 `--page`와 `--size` 플래그를 지원해야 한다(SHALL).

#### Scenario: 특정 페이지 조회
- **WHEN** `storectl product list --page 2 --size 20`을 실행하면
- **THEN** 2페이지의 20개 상품을 표시하고 전체 상품 수와 페이지 정보를 함께 표시해야 한다

### Requirement: 리뷰 목록 페이지네이션
`storectl review list`에 `--page`와 `--size` 플래그를 지원해야 한다(SHALL).

#### Scenario: 리뷰 페이지 조회
- **WHEN** `storectl review list --page 1 --size 5`를 실행하면
- **THEN** 첫 페이지의 5개 리뷰를 표시하고 총 리뷰 수와 페이지 정보를 표시해야 한다
