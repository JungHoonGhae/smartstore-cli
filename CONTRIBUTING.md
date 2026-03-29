# Contributing to smartstore-cli

smartstore-cli에 기여해주셔서 감사합니다!

## Getting Started

```bash
# Fork & clone
git clone https://github.com/<your-username>/smartstore-cli.git
cd smartstore-cli

# Build
make build

# Auth helper (Python 3.11+)
pip install -e auth-helper/

# Test
make test

# Check system
bin/storectl doctor
```

## Development Workflow

1. `main` 브랜치에서 feature 브랜치 생성
2. 코드 수정 + 테스트 작성
3. `make build && make test && make fmt` 통과 확인
4. PR 생성

## Project Structure

```
cmd/storectl/       CLI 커맨드 (Cobra)
internal/
  auth/             브라우저 로그인 오케스트레이션
  client/           네이버 스마트스토어 웹 API 클라이언트
  config/           설정 로드 & 경로
  doctor/           시스템 헬스 체크
  domain/           데이터 모델 (실제 API 응답 매핑)
  output/           멀티포맷 렌더러 (table/JSON/CSV)
  session/          세션 영속성 + 자동 갱신
  version/          빌드 버전 정보
auth-helper/        Python + Playwright 로그인 헬퍼
```

## Code Conventions

- **Go**: `gofmt` 적용, 에러는 항상 처리
- **커밋 메시지**: 영어 권장, 한글 OK. 첫 줄은 동사로 시작 (Add, Fix, Update)
- **읽기 전용 원칙**: 모든 커맨드는 기본적으로 read-only. 쓰기 기능은 별도 config 토글 필요
- **테스트**: 새 기능 추가 시 테스트 필수. `go test ./...` 통과 확인

## API Reverse Engineering

새로운 API 엔드포인트를 추가하려면:

1. Chrome DevTools 또는 `/browse`로 판매자센터 트래픽 캡처
2. `fixtures/responses/`에 응답 샘플 저장
3. `internal/domain/models.go`에 응답 모델 추가
4. `internal/client/`에 API 메서드 추가
5. `internal/output/`에 포맷터 추가
6. `cmd/storectl/`에 CLI 커맨드 추가
7. `docs/api/CHANGELOG.md`에 발견 내용 기록

가이드: [`docs/reverse-engineering/capture-guide.md`](docs/reverse-engineering/capture-guide.md)

## Session & Cookie Notes

- `CBI_CHK` 쿠키는 `"` 문자를 포함할 수 있음 → Go `net/http`에서 strip 필요
- `kit.session`은 `center.shopping.naver.com` 도메인 → Python `requests`에서 도메인 주의
- 세션 만료 시 `change-channel` + `login/init` 플로우로 자동 복구
- Playwright는 시스템 Chrome 사용 (`channel="chrome"`)

## Reporting Issues

- 버그 리포트: 재현 단계 + `storectl doctor` 출력 포함
- API 변경 감지: `scripts/diff-api.py`로 HAR 비교 결과 첨부

## License

기여한 코드는 [MIT License](LICENSE)로 배포됩니다.
