# AGENTS.md
#
# [역할] AI 코딩 에이전트를 위한 범용 프로젝트 지침 파일 (오픈 표준)
#
# [읽는 도구] OpenAI Codex, GitHub Copilot, Google Gemini CLI, Sourcegraph Amp,
#             Roo Code, Zed 등 — Claude Code는 아직 미지원 (CLAUDE.md 사용)
#
# [CLAUDE.md와 차이] 내용은 동일한 역할. 읽는 도구가 다를 뿐.
#   - CLAUDE.md → Claude Code 전용
#   - AGENTS.md → 여러 AI 도구가 읽는 범용 표준
#   - 팀에서 여러 AI 도구를 쓴다면 AGENTS.md를 메인으로 작성하고
#     CLAUDE.md는 심링크(ln -s AGENTS.md CLAUDE.md)하는 것이 권장됨
#
# [작성 가이드] 효과적인 AGENTS.md는 6가지를 포함:
#   1. Commands — 빌드/테스트/린트 명령어 (플래그까지 정확히)
#   2. Testing — 테스트 프레임워크, 실행 방법
#   3. Project structure — 디렉토리/파일 역할
#   4. Code style — 코딩 컨벤션 (예시 코드 포함)
#   5. Git workflow — 브랜치, 커밋 메시지, PR 규칙
#   6. Boundaries — AI가 절대 하면 안 되는 것 (always/ask/never)
#
# [참고]
#   - 공식 사이트: https://agents.md/
#   - GitHub: https://github.com/agentsmd/agents.md
#   - 가이드: https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
#
# TODO: 다른 AI 도구를 함께 사용할 때 아래에 프로젝트 지침 작성
