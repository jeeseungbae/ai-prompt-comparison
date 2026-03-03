# AGENTS.md -- 주택청약 디스코드 봇

## Project Overview
Python 디스코드 봇으로, data.go.kr 한국부동산원 청약홈 API를 연동하여
주택청약 분양정보/경쟁률/당첨통계를 조회하고 신규 공고를 자동 알림합니다.

## Key Directories
- `bot/` -- 메인 봇 코드
- `bot/cogs/` -- Discord 명령어 Cog 모듈 (subscription, competition, notification)
- `bot/services/` -- 비즈니스 로직 (api_client, formatter, database)
- `bot/api/` -- FastAPI 헬스체크
- `tests/` -- pytest 테스트

## Entry Point
`bot/main.py` -- discord.py 봇과 FastAPI 서버를 asyncio로 동시 실행

## Setup Commands
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env에 DISCORD_TOKEN, DATA_GO_KR_API_KEY 입력
python -m bot.main
```

## Code Style
- Python 3.12 features OK (match statement, StrEnum 등)
- Type hints 모든 함수에 필수
- Docstring 한국어
- loguru for logging (stdlib logging 사용 금지)
- ruff for linting/formatting (`ruff check . && ruff format .`)
- 최대 줄 길이 100자

## Code Review Standards
- 모든 함수에 type hints 있는지 확인
- async 함수에서 blocking I/O 사용하지 않는지 확인
- API 키가 하드코딩되어 있지 않은지 확인
- 에러 처리가 누락된 외부 API 호출이 없는지 확인
- Discord Embed 텍스트가 한국어인지 확인
- Pydantic v2 문법만 사용하는지 확인

## Testing
- Framework: pytest + pytest-asyncio (strict mode)
- async 테스트: `@pytest.mark.asyncio` 데코레이터 필수
- async fixture: `@pytest_asyncio.fixture` 사용
- API mock: aioresponses 또는 unittest.mock
- 실행: `python -m pytest tests/ -v`
- 최소 커버리지: api_client, formatter 단위 테스트

## Code Quality
- ruff 린트 통과 필수: `ruff check .`
- ruff 포맷 통과 필수: `ruff format --check .`
- import 정렬: ruff isort 규칙 적용
- 미사용 import/변수 제거

## Development Order
1. config.py + .env.example (설정 먼저)
2. services/api_client.py (데이터 소스 연결)
3. services/formatter.py (표시 형식)
4. services/database.py (상태 저장)
5. cogs/subscription.py (조회 명령어)
6. cogs/competition.py (경쟁률 명령어)
7. cogs/notification.py (자동 알림)
8. api/health.py (헬스체크)
9. main.py (통합)
10. tests/ (검증)
11. pyproject.toml, requirements.txt, .gitignore, README.md

## Git Workflow
- Feature branches from main
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

## Boundaries

### Always
- None/null API 응답 graceful 처리
- 모든 I/O에 async/await 사용
- Type hints 포함
- 한국어 사용자 메시지
- API 호출 실패 시 재시도 (3회, exponential backoff)

### Ask First
- 새 의존성 추가
- 디렉토리 구조 변경
- DB 스키마 변경

### Never
- 시크릿 하드코딩
- async 코드에서 blocking I/O
- API 호출 에러 처리 생략
- .env 파일 커밋
- Pydantic v1 문법 사용
- serviceKey를 로그/메시지에 노출

## Special Considerations
- data.go.kr serviceKey는 URL 인코딩 필수 (+, = 문자 포함)
- 분양정보 날짜: YYYY-MM-DD, 당첨통계 날짜: YYYYMM (형식 다름)
- API 빈 응답: `{"currentCount":0,"data":[]}`
- discord.py hybrid_command 사용 시 `await ctx.defer()` 호출 (슬래시 3초 타임아웃 방지)
- on_ready()에서 tree.sync() 호출 금지 -- 별도 sync 명령어 사용
