# 주택청약 디스코드 봇 — Project Instructions

## Overview
주택청약(아파트 분양) 정보를 실시간으로 조회하고 알림받는 디스코드 봇.
data.go.kr 한국부동산원 청약홈 API를 연동하여 분양공고, 경쟁률, 당첨자 통계를 제공한다.

## Tech Stack
Python 3.12 기반. 패키지 버전은 `requirements.txt` / `requirements-dev.txt` 참고.
설치 후 패키지 간 호환성 문제가 있으면 확인하고 수정할 것.

## 필수 참조 문서
이 프로젝트의 모든 AI 에이전트는 아래 문서를 반드시 읽고 따라야 한다:
- `.claude/AGENTS.md` — 에이전트 역할 분담 및 워크플로우
- `.claude/rules/architecture.md` — 레이어 구조, 디렉토리 규칙
- `.claude/rules/security.md` — 보안 규칙, 인증, 환경변수
- `.claude/rules/api.md` — 청약홈 API 연동 스펙
- `.claude/rules/quality.md` — 코드 스타일, 테스트, 에러 처리

## Project Structure
```
bot/
├── main.py          # Entry point: bot + FastAPI 동시 실행 (asyncio.gather)
├── config.py        # Settings (.env 로딩)
├── models.py        # Pydantic 모델
├── cogs/            # 프레젠테이션 레이어: 사용자 입력/출력만 담당
├── services/        # 비즈니스 레이어: API 호출, 데이터 가공, DB 접근
└── api/             # 헬스체크 엔드포인트
tests/               # pytest 단위 테스트
```

## Environment Variables
```
DISCORD_TOKEN=           # 필수
DATA_GO_KR_API_KEY=      # 필수
NOTIFICATION_CHANNEL_ID= # 알림 채널 ID
CHECK_INTERVAL_MINUTES=30
DATABASE_PATH=./data/bot.db
LOG_LEVEL=INFO
```

## Development Workflow
1. config.py와 .env.example 작성
2. services/ 레이어 구현
3. cogs/ 구현
4. main.py에서 봇 + FastAPI 통합
5. tests/ 작성
6. pyproject.toml, requirements.txt, .gitignore 마무리

## Execution Mode — 멀티에이전트 필수

이 프로젝트의 모든 작업은 멀티에이전트 오케스트레이션으로 수행한다.
단일 에이전트로 순차 작업하지 않는다.

### 필수 워크플로우
1. 어떤 요청이든 `.claude/AGENTS.md`의 워크플로우를 따른다
2. 코드 작성은 반드시 executor 에이전트에게 위임한다
3. 독립적인 작업(services/ 구현, cogs/ 구현)은 병렬로 실행한다
4. 구현 완료 후 qa-tester, security-reviewer를 동시에 실행한다
5. 모든 작업 완료 후 architect가 최종 승인해야 완료로 간주한다

### 에이전트 모델 배정
- architect: opus (설계/검토는 정확성이 중요)
- executor: sonnet (구현은 속도와 품질 균형)
- qa-tester: sonnet
- security-reviewer: sonnet
- 단순 조회/탐색: haiku

## Never
- API 키 하드코딩
- .env 파일 커밋
- async 컨텍스트에서 blocking I/O (requests, time.sleep 등)
- API rate limit 무시
- serviceKey를 Discord 메시지나 로그에 노출
- 단일 에이전트로 전체 프로젝트를 순차 구현
- architect 승인 없이 작업 완료 선언
