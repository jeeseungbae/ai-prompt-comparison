# Agent Delegation Rules

## 워크플로우

모든 기능 개발은 아래 순서를 따른다. 단계를 건너뛰지 않는다.

```
1. architect   → 구조 설계 및 파일 배치 결정
2. executor    → 코드 구현 (services/ 와 cogs/ 병렬 가능)
3. qa-tester   → 테스트 작성 및 실행
4. security    → API 키 노출, 입력 검증 확인
5. architect   → 최종 검토 및 승인
```

## 에이전트별 역할

### architect (설계자)
- 새 기능 추가 시 **반드시 먼저** 호출
- 파일 배치, 레이어 분리, 의존 방향 결정
- 최종 검토 시 레이어 규칙 위반 여부 확인
- architect 승인 없이 완료 선언 금지

### executor (구현자)
- architect가 결정한 구조대로 코드 작성
- `.claude/rules/` 아래 모든 규칙 파일을 읽고 준수

### qa-tester (검증자)
- 구현 완료된 코드에 대해 pytest 테스트 작성
- 테스트 실패 시 executor에게 수정 요청
- 테스트/린트 기준은 `rules/quality.md` 참조

### security-reviewer (보안 검토자)
- `rules/security.md` 기준으로 보안 위반 여부 확인

## 병렬 실행 규칙
- 독립적인 레이어(services/, cogs/)는 동시 진행 가능
- tests/와 security 검토는 구현 완료 후 동시 진행 가능
- architect 최종 검토는 모든 작업 완료 후

## 에이전트 간 규칙
- executor는 architect의 설계를 변경하지 않는다
- qa-tester가 발견한 버그는 executor가 수정한다
- security-reviewer가 발견한 이슈는 executor가 수정한다
- 의견 충돌 시 architect가 최종 결정
