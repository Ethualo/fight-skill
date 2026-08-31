# fight-skill 작업 지침

Codex 유지보수 지침이다. 플러그인은 Claude Code와 Codex 양쪽을 지원하며 외부 모델 provider, CLI, MCP에 의존하지 않는다.

Claude Code 설치와 공통 개요는 [CLAUDE.md](CLAUDE.md)를 참고한다. `skills/*/SKILL.md`는 두 플랫폼이 공유하는 단일 본문이며, 서브에이전트 호출 계약만 플랫폼별로 분기한다 — Codex는 subagent spawn 도구, Claude Code는 `Agent` 툴.

## 구조

- `.codex-plugin/plugin.json`: Codex 플러그인 매니페스트
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`: Claude Code 플러그인·마켓플레이스 매니페스트
- `hooks/`: Claude Code 전용 SessionStart 훅. Codex는 사용하지 않음
- `skills/fight-audit/`: 제안자·감사자 비대칭 검증 프로토콜 (양 플랫폼 공유)
- `skills/fight-clarify/`: 양극단 해석 병렬 분기 프로토콜 (양 플랫폼 공유)
- `docs/superpowers/`: 설계 스펙과 최초 Claude Code 구현 계획. 역할 구조(비대칭·대칭)의 근거는 지금도 유효하다

## 실행 및 검증

### 정적 검증

- Codex 플러그인 검증: `python C:\Users\user\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .`
- 스킬 검증: `python -X utf8 C:\Users\user\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\fight-audit`
- 스킬 검증: `python -X utf8 C:\Users\user\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\fight-clarify`

### 라이브 검증

- Codex와 Claude Code 각각에서 두 스킬을 실제 호출해 subagent 수·순서·출력을 확인한다.
- 감사자는 파일·줄 또는 명령 근거와 구체적 실패 시나리오를 남겨야 한다.
- 해석자는 같은 메시지에서 병렬 실행하고, 두 안의 공통점은 묻지 않는다.

## 환경

- Windows 10, PowerShell 우선
- 외부 환경변수 없음
- Codex 모델 서열: `sol` > `terra` > `luna`. reasoning effort는 `low`/`medium`/`high`/`xhigh`/`max`/`ultra` 6단계
- Codex 서브에이전트 모델: fight-audit은 제안자 `gpt-5.6-terra`(reasoning `xhigh`) / 감사자 `gpt-5.6-sol`(reasoning `medium`, 비용 절감 실험 중 — 벤더 권장은 `max`, 실측 후 조정) 고정(감사자만 상위 모델 — 근거는 `skills/fight-audit/SKILL.md` 2단계), fight-clarify는 두 호출 모두 `gpt-5.6-luna`(reasoning `max`, 대칭 구조라 열화 리스크 없고 해석 작업 자체가 "명확한 구현" 범주)
- Claude Code 서브에이전트 모델: fight-audit은 제안자 `sonnet` / 감사자 `opus` 고정, fight-clarify는 미고정(부모 세션 모델 상속) — 근거는 `skills/fight-audit/SKILL.md` 2단계 참고

## 주요 패턴

- 스킬당 서브에이전트 호출은 정확히 2회
- `fight-audit`은 순차 호출, `fight-clarify`는 같은 메시지에서 병렬 호출
- Codex 서브에이전트는 `fork_context: false`로 메인 대화 추론을 상속하지 않음
- 판정과 사용자 질문은 메인 스레드가 담당
- 한국어 본문과 기존 태그·출력 형식을 유지

## 주의사항

- 외부 provider·CLI·MCP fallback을 추가하지 않음
- 지정 모델을 사용할 수 없으면 조용히 다른 모델로 대체하지 않고 중단
- `skills/*/SKILL.md` 변경 시 두 플랫폼 매니페스트(`.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`) 버전을 모두 올리고 재검증
- 감사자의 근거 없는 통과나 실패 시나리오 없는 지적을 허용하지 않음
- 설치된 Claude Code 플러그인은 `~/.claude/plugins/cache/fight/fight/{version}/`의 버전별 스냅샷 복사본이다. 저장소 편집만으로는 실행 중인 내용이 바뀌지 않는다 — 버전을 올리고 `claude plugin update fight@fight`를 실행해야 반영된다

<!-- handoff:learnings:begin -->
## Session Learnings (auto-updated by handoff)

### Implicit Rules
- Windows 10; PowerShell primary; use python, not python3; Node.js at C:\Program Files\nodejs\node.exe; no jq.
- User-facing and project documentation prose Korean; preserve frontmatter keys, JSON keys, tool names, severity tags, and assumption tags.
- Shared skills remain platform-neutral except invocation-contract branches; exactly two subagents per skill; fight-audit sequential; fight-clarify same-message parallel; main thread judges.
- Codex subagents use fork_context=false with explicit model and reasoning; unavailable models never silently replaced.
- No external provider, CLI, or MCP fallback; skill changes require both manifest version bumps and validator reruns.
- Claude Code runs versioned installed cache snapshots; worktree edits are not installation proof; refresh cache before Claude live claims.
- Preserve unrelated WIP; distinguish edited, validated, committed, installed, and published states.

### Key Decisions
- Decision: support Claude Code and Codex — Reason: preserve user-required dual-platform compatibility.
- Decision: keep one shared SKILL.md protocol body per skill, branch only invocation contracts — Reason: preserve identical verification rules while adapting Agent versus Codex spawn mechanisms.
- Decision: Codex fight-audit proposer gpt-5.6-terra xhigh and auditor gpt-5.6-sol medium — Reason: retain model heterogeneity while measuring cost versus audit rigor; current medium run preserved evidence and failure-scenario gates.
- Decision: Codex fight-clarify uses two gpt-5.6-luna max calls in the same message — Reason: symmetric interpretation requires parallel divergence without cross-review.
- Decision: restrict current documentation work to AGENTS.md and CLAUDE.md — Reason: user selected minimal scope; defer README, public docs, and marketplace expansion.
- Decision: keep plugin version 0.3.6 — Reason: current changes are documentation-only; skills and manifests unchanged.
- Decision: preserve manual WIP and auto-managed handoff blocks — Reason: avoid overwriting user changes and keep future resume context bounded.

<!-- handoff:learnings:end -->
