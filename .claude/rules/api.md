# API Integration Rules

## Base Config
- Base URL: `https://api.odcloud.kr/api`
- Auth: query param `serviceKey={API_KEY}` (URL-encoded 필수 — +, = 문자 포함)
- Pagination: `page=1&perPage=10` (max 1000)
- Rate limit: 일 1,000건 (개발계정)

## Endpoints

### 분양정보 (15098547)
- `GET /ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail`
- Filter: `cond[RCRIT_PBLANC_DE::GTE]=YYYY-MM-DD`
- Key fields: HOUSE_MANAGE_NO, PBLANC_NO, HOUSE_NM, HSSPLY_ADRES, RCRIT_PBLANC_DE, PRZWNER_PRESNATN_DE, CNSTRCT_ENTRPS_NM

### 경쟁률 (15098905)
- `GET /ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet`
- Filter: `cond[HOUSE_MANAGE_NO::EQ]`, `cond[PBLANC_NO::EQ]`
- Key fields: HOUSE_TY, SUPLY_HSHLDCO, SUPLY_REQ_CNT, SUPLY_CMPET_RATE

### 당첨통계 (15110812)
- `GET /ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat`
- Filter: `cond[STAT_DE::GTE]=YYYYMM` (주의: 날짜 형식 다름 — YYYYMM)
- Key fields: SUBSCRPT_AREA_CODE_NM, AGE_30, AGE_40, AGE_50, AGE_60

## API 응답 구조
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

## 호출 규칙
- 모든 외부 호출은 aiohttp 비동기 필수
- 실패 시 3회 재시도 exponential backoff (1s, 2s, 4s)
- 재시도 초과 시 사용자에게 한국어로 안내
- aiohttp 세션은 봇 시작 시 생성, 종료 시 close

## 명령어 매핑
| 명령어 | API | 설명 |
|--------|-----|------|
| `/청약 최신` | 분양정보 | 최근 분양공고 5건 |
| `/청약 검색 [키워드]` | 분양정보 | 주택명 검색 |
| `/청약 상세 [공고번호]` | 분양정보 | 공고 상세 |
| `/경쟁률 [공고번호]` | 경쟁률 | 주택형별 경쟁률 |
| `/당첨통계 [지역]` | 당첨통계 | 지역별 당첨자 통계 |
| `/알림설정` | - | 현재 채널을 알림 채널로 등록 |
| `/도움말` | - | 사용법 안내 |
