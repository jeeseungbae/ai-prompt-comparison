# Case 2: 상세한 프롬프트

## 실행 방법
1. 이 브랜치(`case2`)에서 새 Claude Code 세션을 엽니다
2. 아래 프롬프트를 그대로 복사해서 붙여넣습니다
3. Claude가 끝날 때까지 추가 입력 없이 기다립니다

## 프롬프트

주택청약 정보 디스코드 봇을 Python으로 만들어줘.

기술스택: Python 3.12, discord.py 2.7.0 (hybrid_command), FastAPI 0.135.1, aiohttp, aiosqlite, python-dotenv, loguru

data.go.kr 한국부동산원 청약홈 API 3개를 연동해야 해:
- 분양정보 (15098547): /ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail
- 경쟁률 (15098905): /ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet
- 당첨통계 (15110812): /ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat
Base URL은 https://api.odcloud.kr/api 이고 serviceKey 쿼리파라미터로 인증해.

디스코드 명령어는 /청약 최신, /청약 검색, /청약 상세, /경쟁률, /당첨통계, /알림설정, /도움말 이렇게 7개.

30분마다 새 공고 체크해서 자동 알림 보내는 기능도 있어야 하고, 마지막 체크한 공고 ID는 SQLite에 저장해줘.

bot/cogs/ 에 명령어 Cog 분리하고, bot/services/ 에 API 클라이언트랑 포맷터 분리해줘. 테스트 코드도 만들고, .env.example이랑 .gitignore도 포함시켜줘. 에러 처리는 API 호출 실패 시 3회 재시도하고, 사용자한테 보여주는 메시지는 전부 한국어로 해줘.

프로젝트 전체를 처음부터 끝까지 다 만들어줘.
