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
- Installed Claude Code plugin marketplaces with a Git source live as real git clones at ~/.claude/plugins/marketplaces/{marketplace-name}; `claude plugin update <plugin>@<marketplace>` decides whether to update by reading THAT LOCAL CLONE's checked-out .claude-plugin/plugin.json version (it does not itself fetch/pull) — so a stale or diverged clone silently blocks updates even when the source repo has a newer version.
- `claude plugin marketplace update <name>` can print 'Successfully updated marketplace: <name>' without actually fast-forwarding the clone's local branch, if that local branch has diverged (non-fast-forward) from origin — always verify afterward with `git -C ~/.claude/plugins/marketplaces/<name> log`/plugin.json content, never trust the success message alone.
- Fix for a stuck/diverged marketplace clone: `git -C <clone> fetch origin && git -C <clone> reset --hard origin/<default-branch>` — safe because it is a pure install-cache clone, never real user work, then retry `claude plugin update <plugin>@<marketplace>`.
- A successful `claude plugin update` still requires restarting Claude Code before the new plugin version is actually loaded into a running session.
- origin/dev's git history was rewritten/rebased at some point after commit e7084a6 during this project's work, orphaning an earlier merge-commit-based ancestry (3248e20, 0438f47, 0259c8c) from the new origin/dev tip even though those exact commit objects remain reachable locally — this is why a marketplace clone cloned before the rewrite shows as 'diverged' rather than simply 'behind'.
- Codex reasoning effort has exactly 6 levels: low/medium/high/xhigh/max/ultra (corrects a previously-recorded wrong 5-level light/medium/high/extra-high/max).

### Key Decisions
- Decision: Correct Codex reasoning-effort enumeration to low/medium/high/xhigh/max/ultra (6 levels) — Reason: user supplied this as the actual supported value set, replacing a previously-recorded wrong 5-level light/medium/high/extra-high/max.
- Decision: Keep existing model/effort pins unchanged except the effort-level rename (extra-high→xhigh) — Reason: only the label was wrong, not the underlying pinned level; live Codex runs this session confirmed sol+medium still meets the evidence/failure-scenario bar.
- Decision: Record per-scenario (1/2/3) x per-platform (Claude Code/Codex) pass status directly in CLAUDE.md's 검증 section as a table — Reason: user asked to make completion status explicit rather than leaving it only in ephemeral handoff summaries.
- Decision: Keep scenario 1's Codex result worded precisely as 'executed, ended in a valid BLOCK because the test proposal had a real defect' rather than flattening to a plain pass — Reason: user explicitly chose accuracy ('유지 및 커밋') over a uniform-looking table.
- Decision: Do not duplicate the new scenario-status table into AGENTS.md — Reason: user declined when asked; AGENTS.md keeps a narrower Codex-maintenance scope.
- Decision: Remove CLAUDE.md's own Codex model-policy table row and point to AGENTS.md as single source instead — Reason: a concurrent Codex-session edit deduplicated this; reviewed and kept as a legitimate simplification.
- Decision: Force-sync the stale ~/.claude/plugins/marketplaces/fight git clone via fetch + reset --hard origin/dev — Reason: user approved after confirmation it's a pure install-cache clone (not real work) that had diverged from origin/dev due to an earlier history rewrite.

<!-- handoff:learnings:end -->
