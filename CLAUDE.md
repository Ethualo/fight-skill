# fight

적대적 검증 플러그인. Claude Code와 Codex 양쪽을 지원한다. 실행 코드 없음. 프로토콜 문서와 훅만 있다.

Codex 유지보수·모델·검증 명령은 [AGENTS.md](AGENTS.md)를 참고한다. 스킬 본문(`skills/*/SKILL.md`)은 두 플랫폼이 공유하며, 호출 계약(서브에이전트 스폰 방식)만 플랫폼별로 분기한다.

## 설치 (Claude Code)

```
/plugin marketplace add C:\Users\user\Desktop\git_projects\fight-skill
/plugin install fight@fight
```

## 구조

| 경로 | 역할 |
|---|---|
| `.claude-plugin/plugin.json` | Claude Code 플러그인 매니페스트 |
| `.claude-plugin/marketplace.json` | 마켓플레이스 매니페스트. 설치 진입점 |
| `.codex-plugin/plugin.json` | Codex 플러그인 매니페스트 |
| `AGENTS.md` | Codex가 읽는 작업 지침. 이 파일의 Codex 쪽 대응물 |
| `skills/fight-audit/SKILL.md` | 제안자·감사자 비대칭 검증. 순차 2회 호출. 양 플랫폼 공유 |
| `skills/fight-clarify/SKILL.md` | 양극단 해석 분기. 병렬 2회 호출. 양 플랫폼 공유 |
| `hooks/hooks.json` | SessionStart 훅 정의 (Claude Code 전용, Codex는 사용 안 함) |
| `hooks/askuserquestion-rule.md` | 훅이 주입하는 규칙 전문 |
| `docs/superpowers/specs/` | 설계 스펙 (플랫폼 공통 근거) |
| `docs/superpowers/plans/` | 최초 Claude Code 구현 계획 (역사 기록) |

## 설계 근거

`fight-audit`은 비대칭, `fight-clarify`는 대칭이다. 비대칭은 편향을, 대칭은 분산을 잡는다.
같은 모델 두 개로 대칭을 구성하면 동조 방지가 원리적으로 성립하지 않는다.
자세한 근거는 스펙 2절 "결정: 역할 구조"에 있다.

## 모델 정책

| 플랫폼 | `fight-audit` | `fight-clarify` |
|---|---|---|
| Claude Code | 제안자 `sonnet`, 감사자 `opus` | 부모 세션 모델 상속 |

Codex 모델·reasoning·`fork_context`·fallback 정책은 [AGENTS.md](AGENTS.md)의 환경과 주요 패턴을 기준으로 한다.

두 플랫폼 모두 외부 provider·CLI·MCP를 사용하지 않으며, 지정 모델을 사용할 수 없을 때 조용히 대체하지 않는다.

## 주의사항

- **서브에이전트 호출은 스킬당 정확히 2회.** 라운드를 늘리면 비용만 두 배가 되고 판정은 거의 바뀌지 않는다.
- **판정은 메인 스레드가 한다.** 심판 서브에이전트를 추가하지 마라. 메인만 대화 히스토리와 코드베이스 컨텍스트를 가진다.
- **감사자의 보고 규칙을 완화하지 마라.** 실패 시나리오를 요구하는 조항이 억지 반대를 막는 유일한 장치다.
- **감사자에게 "이의 없음"을 허용해야 한다.** 매번 무언가를 내라고 강제하면 그 자체가 억지 반대다.
- **`fight-clarify`는 축을 하나만 고른다.** 두 개 이상 벌리면 두 안의 차이를 읽을 수 없다.
- **훅은 Node.js에 의존한다.** `cat`은 Windows `cmd`에 없고 `echo`는 UTF-8 여러 줄을 깨뜨려서 `node`를 쓴다. 플러그인 루트 경로는 `process.env.CLAUDE_PLUGIN_ROOT`로 읽지 않고 `${CLAUDE_PLUGIN_ROOT}`를 커맨드 문자열에 그대로 넣어 `argv`로 넘긴다. Claude Code가 셸에 넘기기 전에 문자열 치환을 하므로 환경변수 미설정에 영향받지 않는다.
- 스킬 본문을 고치면 `plugin.json`의 patch 버전을 올린다.

## 검증

단위 테스트가 없다. 실행 로직이 없기 때문이다. 검증은 실제 호출로 한다.
계획 문서의 시나리오 1–3을 그대로 다시 돌린다.

| 시나리오 | 내용 | Claude Code | Codex |
|---|---|---|---|
| 1 | 타당한 지시 → 감사자가 "이의 없음"과 근거 여섯 줄을 반환한다 | 통과 | 실행됨 (제안안 `BLOCK`, 정상 기준 미달) |
| 2 | 결함 있는 지시 → 구체적 실패 시나리오와 함께 `BLOCK`이 나온다 | 통과 | 통과 |
| 3 | 모호한 지시 → 두 안이 실제로 갈리고, 일치 부분은 유저에게 묻지 않는다 | 통과 | 통과 |

Codex 시나리오 1은 감사자가 여섯 축·근거·실패 시나리오를 모두 출력했지만, 제안안의 결함 때문에 `이의 없음`이 아니라 유효한 `BLOCK`으로 끝났다. 시나리오 2와 3은 기대 결과를 확인했다.

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
