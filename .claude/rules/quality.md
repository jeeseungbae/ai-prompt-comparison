# Code Quality Rules

## 코드 스타일
- Type hints 모든 함수에 필수
- Docstring 한국어로 작성
- `loguru.logger` 사용 (stdlib logging 금지)
- Pydantic v2 전용: `model_validate()`, `model_dump()`, `model_config = ConfigDict(...)`
- 사용자 대면 에러 메시지는 한국어, 친절한 톤

## 에러 처리
- API 호출 재시도 규칙은 `api.md` 참조
- Discord 명령어 에러: 한국어 Embed로 사용자에게 안내
- 비즈니스 에러: 커스텀 Exception + HTTP 상태코드 매핑
- 예상 외 에러: global exception handler로 일괄 처리
- 에러 응답 포맷: `{"error": str, "code": str, "detail": any}`

## 테스트
- pytest-asyncio strict 모드
- async 테스트에 `@pytest.mark.asyncio`
- async fixture에 `@pytest_asyncio.fixture`
- 외부 API 호출은 반드시 mock 처리
- 완료 후 `ruff check . && ruff format --check .`로 린트 통과 확인

## Scheduled Tasks
- `@tasks.loop`로 주기적 새 공고 체크
- 체크 주기: 환경변수 `CHECK_INTERVAL_MINUTES` (기본 30분)
- SQLite에 마지막 HOUSE_MANAGE_NO 저장하여 새 공고 감지
- 스케줄러 실패: 다음 주기에 자동 재시도 (봇 크래시 방지)

## Graceful Shutdown
- SIGTERM 시 aiohttp 세션, DB 커넥션 정리 후 종료
- 봇 시작: 명령어 트리 동기화 포함 30초 이내
