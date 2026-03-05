# Architecture Rules

## 레이어 구조 및 책임

### cogs/ (프레젠테이션 레이어)
- 사용자 입력 파싱, services/ 호출, 결과를 Embed로 응답
- **금지**: 직접 API 호출, DB 접근, 비즈니스 로직

### services/ (비즈니스 레이어)
- API 호출, 데이터 가공, DB 접근 전담
- **금지**: Discord 객체(ctx, Embed 등) 의존

### 의존 방향
- cogs → services (단방향만 허용)
- services 간 순환 의존 금지
- api_client → formatter 방향만 허용

## 데이터 규칙
- API 응답은 **반드시 Pydantic 모델**로 매핑 (raw dict 사용 금지)
- API에서 가져온 데이터를 DB에 중복 저장하지 않음
- DB는 알림 추적용 메타데이터만 저장 (HOUSE_MANAGE_NO, guild_id, channel_id)
- 분양정보/경쟁률/당첨통계는 항상 API에서 실시간 조회

## 성능 기준
- 디스코드 명령어 응답: 3초 이내 (defer 호출)
- 외부 API 호출 타임아웃: 10초
- DB 쿼리: 100ms 이내 (인덱스 활용)
- aiohttp 세션: 봇 생명주기와 동일, 커넥션 풀 재사용
- SQLite: 단일 커넥션 재사용 (WAL 모드)

## Discord Bot Patterns
- 모든 명령어는 `@commands.hybrid_command` (슬래시 + 텍스트 동시 지원)
- 느린 명령어는 반드시 `await ctx.defer()` 호출
- Embed Color: `0x0066FF` info, `0xFF3333` error, `0x00CC66` success
- Footer: "주택청약 봇 | data.go.kr"
- Timestamp 포함
- 사용자 대면 텍스트는 전부 한국어
