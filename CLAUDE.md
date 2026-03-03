# 주택청약 디스코드 봇 -- Project Instructions

## Overview
주택청약(아파트 분양) 정보를 실시간으로 조회하고 알림받는 디스코드 봇.
data.go.kr 한국부동산원 청약홈 API를 연동하여 분양공고, 경쟁률, 당첨자 통계를 제공한다.

## Tech Stack & Versions (정확히 지켜야 함)

| 패키지 | 버전 | 비고 |
|--------|------|------|
| Python | 3.12 | asyncio 최적화, 라이브러리 호환성 최적 |
| discord.py | 2.7.0 | hybrid_command 필수 사용 |
| FastAPI | 0.135.1 | Pydantic v2 전용 (v1 호환 없음) |
| uvicorn | 0.41.0 | `uvicorn[standard]` 설치 |
| aiohttp | 3.13.3 | `aiohttp[speedups]` 권장 |
| aiosqlite | 0.22.1 | |
| pydantic | 2.12.5 | `model_validate()`, `model_dump()` 사용 (parse_obj/dict 금지) |
| python-dotenv | 1.2.2 | Python >=3.10 필수 |
| loguru | 0.7.3 | |
| ruff | 0.15.4 | dev 의존성 |
| pytest | 9.0.2 | dev 의존성 |
| pytest-asyncio | 1.3.0 | strict 모드 기본 -- `@pytest.mark.asyncio` 필수 |

### 패키지 호환성 주의사항
- FastAPI 0.135.1은 Pydantic v1을 지원하지 않음. `class Config:` 대신 `model_config = ConfigDict(...)` 사용
- pytest-asyncio 1.3.0은 strict 모드가 기본. async fixture는 `@pytest_asyncio.fixture` 사용
- aioresponses 0.7.8은 aiohttp 3.11+ 에서 호환 이슈 있음. 테스트 시 주의

## Commands

### Install
```bash
pip install -r requirements.txt
```

### Run
```bash
python -m bot.main
```

### Test
```bash
python -m pytest tests/ -v
```

### Lint
```bash
ruff check . && ruff format --check .
```

## Directory Structure
```
bot/
├── __init__.py
├── main.py              # Entry point: bot + FastAPI 동시 실행 (asyncio.gather)
├── config.py            # Settings dataclass (.env 로딩)
├── cogs/
│   ├── __init__.py
│   ├── subscription.py  # 분양정보 조회 Cog (/청약 최신, /청약 검색, /청약 상세)
│   ├── competition.py   # 경쟁률 조회 Cog (/경쟁률)
│   └── notification.py  # 자동 알림 loop Cog (/알림설정) + tasks.loop
├── services/
│   ├── __init__.py
│   ├── api_client.py    # data.go.kr 비동기 래퍼 (aiohttp)
│   ├── formatter.py     # Discord Embed 포맷터
│   └── database.py      # SQLite 관리 (공고 추적, 알림 채널)
└── api/
    ├── __init__.py
    └── health.py        # FastAPI /health 엔드포인트
tests/
├── __init__.py
├── conftest.py          # pytest fixtures (mock bot, mock api response)
├── test_api_client.py   # API 클라이언트 단위 테스트
└── test_formatter.py    # Embed 포맷터 테스트
```

## API Integration

### Base Config
- Base URL: `https://api.odcloud.kr/api`
- Auth: query param `serviceKey={API_KEY}` (URL-encoded 필수 -- +, = 문자 포함)
- Pagination: `page=1&perPage=10` (max 1000)
- Rate limit: 일 1,000건 (개발계정), 운영은 별도 신청

### Endpoints

**분양정보 (15098547)**
- `GET /ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail`
- Filter: `cond[RCRIT_PBLANC_DE::GTE]=YYYY-MM-DD` (날짜 이후 공고)
- Key fields: HOUSE_MANAGE_NO, PBLANC_NO, HOUSE_NM, HSSPLY_ADRES, RCRIT_PBLANC_DE, PRZWNER_PRESNATN_DE, CNSTRCT_ENTRPS_NM

**경쟁률 (15098905)**
- `GET /ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet`
- Filter: `cond[HOUSE_MANAGE_NO::EQ]`, `cond[PBLANC_NO::EQ]`
- Key fields: HOUSE_TY, SUPLY_HSHLDCO, SUPLY_REQ_CNT, SUPLY_CMPET_RATE

**당첨통계 (15110812)**
- `GET /ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat`
- Filter: `cond[STAT_DE::GTE]=YYYYMM` (주의: 날짜 형식 다름)
- Key fields: SUBSCRPT_AREA_CODE_NM, AGE_30, AGE_40, AGE_50, AGE_60

### API 응답 구조
```json
{
  "currentCount": 10,
  "data": [...],
  "matchCount": 100,
  "page": 1,
  "perPage": 10,
  "totalCount": 100
}
```
빈 결과: `"currentCount": 0, "data": []`

## Discord Bot Patterns

### hybrid_command 필수
모든 명령어는 `@commands.hybrid_command` -- 슬래시 + 텍스트 동시 지원.
느린 명령어는 반드시 `await ctx.defer()` 호출 (슬래시 3초 타임아웃 방지).

### 명령어 목록
| 명령어 | 설명 | 파라미터 |
|--------|------|----------|
| `/청약 최신` | 최근 분양공고 5건 | 없음 |
| `/청약 검색 [키워드]` | 주택명 검색 | keyword: str |
| `/청약 상세 [공고번호]` | 공고 상세 | id: str |
| `/경쟁률 [공고번호]` | 주택형별 경쟁률 | id: str |
| `/당첨통계 [지역]` | 지역별 당첨자 통계 | region: str (optional) |
| `/알림설정` | 현재 채널을 알림 채널로 등록 | 없음 |
| `/도움말` | 사용법 안내 | 없음 |

### Embed Style
- Color: `0x0066FF` info, `0xFF3333` error, `0x00CC66` success
- Footer: "주택청약 봇 | data.go.kr"
- Timestamp 포함
- 사용자 대면 텍스트는 전부 한국어

### Scheduled Tasks
`@tasks.loop(minutes=30)` in notification.py.
SQLite에 마지막 HOUSE_MANAGE_NO 저장하여 새 공고 감지.

## Environment Variables
```
DISCORD_TOKEN=           # 필수
DATA_GO_KR_API_KEY=      # 필수
NOTIFICATION_CHANNEL_ID= # 알림 채널 ID
CHECK_INTERVAL_MINUTES=30
DATABASE_PATH=./data/bot.db
LOG_LEVEL=INFO
```

## Code Style Rules
- Type hints 모든 함수에 필수
- Docstring 한국어로 작성
- 변수/함수명 영어 snake_case
- `loguru.logger` 사용 (stdlib logging 금지)
- `dataclass` 또는 Pydantic `BaseModel`로 설정 관리 (raw dict 금지)
- 에러 메시지는 한국어, 친절한 톤
- 최대 줄 길이: 100자

## Error Handling
- API 호출: 3회 재시도 exponential backoff (1s, 2s, 4s)
- `aiohttp.ClientError` 명시적 catch
- API 키 미설정: 경고 로그 + 기능 비활성화 (크래시 방지)
- Discord 명령어 에러: 한국어 Embed로 사용자에게 안내

## Development Workflow
1. 먼저 config.py와 .env.example 작성
2. services/ 레이어 구현 (api_client → formatter → database)
3. cogs/ 구현 (subscription → competition → notification)
4. main.py에서 봇 + FastAPI 통합
5. tests/ 작성
6. pyproject.toml, requirements.txt, .gitignore, README.md 마무리

## Test Writing Rules
- `asyncio_mode = "strict"` 사용
- async 테스트: `@pytest.mark.asyncio` 데코레이터 필수
- async fixture: `@pytest_asyncio.fixture` 사용
- API 호출 mock: aioresponses 또는 직접 mock
- 최소한 api_client와 formatter에 대한 단위 테스트 작성

## Never
- API 키 하드코딩 금지
- .env 파일 커밋 금지
- async 컨텍스트에서 blocking I/O 사용 금지 (requests, time.sleep 등)
- API rate limit 무시 금지
- serviceKey를 Discord 메시지나 로그에 노출 금지
- Pydantic v1 문법 사용 금지 (parse_obj, .dict() 등)
