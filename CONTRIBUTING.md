# 기여 가이드

이 저장소는 호스트가 수행하는 프로토콜 문서(`skills/*/SKILL.md`), 규칙 주입 훅(`hooks/`), 매니페스트와 릴리스 검사(`scripts/check_release.py`)로 구성된다.

## 스킬 본문 수정 규칙

- `skills/fight-audit/SKILL.md`, `skills/fight-clarify/SKILL.md`는 Claude Code와 Codex가 공유하는 단일 본문이다. 호출 계약(서브에이전트 스폰 방식)만 플랫폼별로 분기한다 — 프로토콜(프롬프트, 축, 판정 규칙) 자체를 플랫폼별로 다르게 만들지 않는다.
- 스킬 본문을 고치면 `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` 세 버전의 patch를 함께 올리고 `CHANGELOG.md`와 두 README를 갱신한다.
- 감사자의 보고 규칙(실패 시나리오 요구)을 완화하지 않는다. 억지 반대를 막는 유일한 장치다.
- `fight-clarify`는 애매함 축을 하나만 고른다는 제약을 유지한다.

## PR 전 체크리스트

- [ ] 세 매니페스트·README 버전·모델 표·변경 이력 일치 검사: `python -X utf8 scripts/check_release.py`
- [ ] Codex 정적 검증 실행 (`AGENTS.md`의 "정적 검증" 절 명령 참고)
- [ ] 판정·질문 규칙 변경 시 [고정 반례와 정상 흐름](docs/verification/0.3.10.md) 재실행
- [ ] 변경이 스킬 본문에 영향을 준다면, [CLAUDE.md](CLAUDE.md)의 검증 섹션에 있는 시나리오 1–3을 Claude Code와 Codex 양쪽에서 실제로 재현하고 결과를 PR 설명에 첨부
- [ ] 한국어 본문, 기존 태그(`[가정:근거]`/`[가정:공백]`), 출력 형식 유지 확인

## 커밋 메시지

`<type>: <설명>` 형식 (`feat`, `fix`, `docs`, `chore` 등).
