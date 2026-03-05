# Security Rules

## Credential 관리
- 모든 민감 정보는 `.env` 파일에서 로딩 (하드코딩 절대 금지)
- `.env`는 `.gitignore`에 포함, 커밋 금지
- `.env.example`에 키 이름만 기재 (값은 비워둘 것)

## API 키 보호
- `serviceKey`를 Discord 메시지, Embed, 로그에 절대 노출 금지
- 에러 메시지에 API 응답 원문 포함 금지 (파싱된 에러 메시지만 사용)
- 디버그 로그에서도 키 값 마스킹

## 입력 검증
- 사용자 입력(명령어 파라미터)은 Pydantic 모델 또는 명시적 검증 후 사용
- SQL 쿼리에 사용자 입력 직접 삽입 금지 (parameterized query 필수)
- 파일 경로에 사용자 입력 사용 시 path traversal 방지

## 네트워크 보안
- HTTPS만 사용
- 응답 크기 제한 (비정상적으로 큰 응답 차단)
- 타임아웃/비동기 규칙은 `architecture.md`, `api.md` 참조
