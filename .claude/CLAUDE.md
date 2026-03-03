# 주택청약 디스코드 봇 -- Project Instructions

## Overview
주택청약(아파트 분양) 정보를 실시간으로 조회하고 알림받는 디스코드 봇.
data.go.kr 한국부동산원 청약홈 API를 연동하여 분양공고, 경쟁률, 당첨자 통계를 제공한다.

## Tech Stack

Python 3.12 기반. 패키지 버전은 `requirements.txt` / `requirements-dev.txt` 참고.
설치 후 패키지 간 호환성 문제가 있으면 확인하고 수정할 것.

## Architecture

### 레이어 구조 및 책임
```
bot/
├── main.py          # Entry point: bot + FastAPI 동시 실행 (asyncio.gather)
├── config.py        # Settings (.env 로딩)
├── cogs/            # 프레젠테이션 레이어: 사용자 입력/출력만 담당
├── services/        # 비즈니스 레이어: API 호출, 데이터 가공, DB 접근
└── api/             # 헬스체크 엔드포인트
tests/               # pytest 단위 테스트
```

### 레이어 규칙
- **cogs/** → 사용자 입력 파싱, services/ 호출, 결과를 Embed로 응답. 직접 API 호출이나 DB 접근 금지
- **services/** → 비즈니스 로직 전담. Discord 객체(ctx, Embed 등) 의존 금지
- **services 간** → 순환 의존 금지. api_client → formatter 방향 단방향만 허용
- API 응답은 Pydantic 모델로 매핑하여 타입 안전성 확보 (raw dict 사용 금지)

### 데이터 규칙
- API에서 가져온 데이터를 DB에 중복 저장하지 않음. DB는 알림 추적용 메타데이터(마지막 공고 ID, 알림 채널)만 저장
- 분양정보/경쟁률/당첨통계 데이터는 항상 API에서 실시간 조회. 로컬 캐시나 복제본 만들지 않음
- DB에 저장하는 것: HOUSE_MANAGE_NO (마지막 체크), guild_id/channel_id (알림 설정)
- DB에 저장하지 않는 것: 공고 상세 내용, 경쟁률 수치, 당첨 통계 등 API 원본 데이터

### 성능 기준

**응답 시간**
- 디스코드 명령어 응답: 3초 이내 (슬래시 커맨드 타임아웃 전 defer 호출)
- 외부 API 호출 타임아웃: 10초 (초과 시 사용자에게 안내)
- DB 쿼리: 100ms 이내 (인덱스 활용)

**리소스 관리**
- aiohttp 세션: 봇 생명주기와 동일. 시작 시 생성, 종료 시 close. 커넥션 풀 재사용
- SQLite 커넥션: 단일 커넥션 재사용 (WAL 모드 권장)
- 메모리: API 응답 캐싱 없음 (rate limit 고려, 매번 fresh 호출)

**안정성**
- 봇 시작: 명령어 트리 동기화 포함 30초 이내
- 스케줄러 실패: 다음 주기에 자동 재시도 (봇 크래시 방지)
- Graceful shutdown: SIGTERM 시 aiohttp 세션, DB 커넥션 정리 후 종료

## API Integration

### Base Config
- Base URL: `https://api.odcloud.kr/api`
- Auth: query param `serviceKey={API_KEY}` (URL-encoded 필수 -- +, = 문자 포함)
- Pagination: `page=1&perPage=10` (max 1000)
- Rate limit: 일 1,000건 (개발계정)

### Endpoints

**분양정보 (15098547)**
- `GET /ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail`
- Filter: `cond[RCRIT_PBLANC_DE::GTE]=YYYY-MM-DD`
- Key fields: HOUSE_MANAGE_NO, PBLANC_NO, HOUSE_NM, HSSPLY_ADRES, RCRIT_PBLANC_DE, PRZWNER_PRESNATN_DE, CNSTRCT_ENTRPS_NM

**경쟁률 (15098905)**
- `GET /ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet`
- Filter: `cond[HOUSE_MANAGE_NO::EQ]`, `cond[PBLANC_NO::EQ]`
- Key fields: HOUSE_TY, SUPLY_HSHLDCO, SUPLY_REQ_CNT, SUPLY_CMPET_RATE

**당첨통계 (15110812)**
- `GET /ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat`
- Filter: `cond[STAT_DE::GTE]=YYYYMM` (주의: 날짜 형식 다름 -- YYYYMM)
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

모든 명령어는 `@commands.hybrid_command` (슬래시 + 텍스트 동시 지원).
느린 명령어는 반드시 `await ctx.defer()` 호출 (슬래시 3초 타임아웃 방지).

### 명령어 목록
| 명령어 | 설명 | 파라미터 |
|--------|------|----------|
| `/청약 최신` | 최근 분양공고 5건 | 없음 |
| `/청약 검색 [키워드]` | 주택명 검색 | keyword: str |
| `/청약 상세 [공고번호]` | 공고 상세 (HOUSE_MANAGE_NO) | id: str |
| `/경쟁률 [공고번호]` | 주택형별 경쟁률 (HOUSE_MANAGE_NO) | id: str |
| `/당첨통계 [지역]` | 지역별 당첨자 통계 | region: str (optional) |
| `/알림설정` | 현재 채널을 알림 채널로 등록 | 없음 |
| `/도움말` | 사용법 안내 | 없음 |

### Embed Style
- Color: `0x0066FF` info, `0xFF3333` error, `0x00CC66` success
- Footer: "주택청약 봇 | data.go.kr"
- Timestamp 포함
- 사용자 대면 텍스트는 전부 한국어

### Scheduled Tasks
`@tasks.loop`로 주기적 새 공고 체크.
체크 주기는 환경변수 `CHECK_INTERVAL_MINUTES`에서 읽음 (기본 30분).
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

## Code Quality

### 코드 스타일
- Type hints 모든 함수에 필수
- Docstring 한국어로 작성
- `loguru.logger` 사용 (stdlib logging 금지)
- Pydantic v2 전용: `model_validate()`, `model_dump()`, `model_config = ConfigDict(...)` 사용
- 사용자 대면 에러 메시지는 한국어, 친절한 톤

### 에러 처리
- API 호출 실패: 3회 재시도 exponential backoff (1s, 2s, 4s)
- Discord 명령어 에러: 한국어 Embed로 사용자에게 안내

### 테스트
- pytest-asyncio strict 모드: async 테스트에 `@pytest.mark.asyncio`, async fixture에 `@pytest_asyncio.fixture`
- 완료 후 `ruff check . && ruff format --check .`로 린트 통과 확인

## Development Workflow
1. config.py와 .env.example 작성
2. services/ 레이어 구현
3. cogs/ 구현
4. main.py에서 봇 + FastAPI 통합
5. tests/ 작성
6. pyproject.toml, requirements.txt, .gitignore 마무리

## Never
- API 키 하드코딩
- .env 파일 커밋
- async 컨텍스트에서 blocking I/O (requests, time.sleep 등)
- API rate limit 무시
- serviceKey를 Discord 메시지나 로그에 노출
- cogs/에서 직접 API 호출이나 DB 접근
- services/에서 Discord 객체(ctx, Embed) 의존
- services 간 순환 의존
- raw dict로 API 응답 처리 (Pydantic 모델 사용)
