# fight

적대적 검증 Claude Code 플러그인. 실행 코드 없음. 프로토콜 문서와 훅만 있다.

## 설치

```
/plugin marketplace add C:\Users\user\Desktop\git_projects\fight-skill
/plugin install fight@fight
```

## 구조

| 경로 | 역할 |
|---|---|
| `.claude-plugin/plugin.json` | 플러그인 매니페스트 |
| `.claude-plugin/marketplace.json` | 마켓플레이스 매니페스트. 설치 진입점 |
| `skills/fight-audit/SKILL.md` | 제안자·감사자 비대칭 검증. 순차 2회 호출 |
| `skills/fight-clarify/SKILL.md` | 양극단 해석 분기. 병렬 2회 호출 |
| `hooks/hooks.json` | SessionStart 훅 정의 |
| `hooks/askuserquestion-rule.md` | 훅이 주입하는 규칙 전문 |
| `docs/superpowers/specs/` | 설계 스펙 |
| `docs/superpowers/plans/` | 구현 계획 |

## 설계 근거

`fight-audit`은 비대칭, `fight-clarify`는 대칭이다. 비대칭은 편향을, 대칭은 분산을 잡는다.
같은 모델 두 개로 대칭을 구성하면 동조 방지가 원리적으로 성립하지 않는다.
자세한 근거는 스펙 2절 "결정: 역할 구조"에 있다.

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

1. 타당한 지시 → 감사자가 "이의 없음"과 근거 여섯 줄을 반환한다.
2. 결함 있는 지시 → 구체적 실패 시나리오와 함께 `BLOCK`이 나온다.
3. 모호한 지시 → 두 안이 실제로 갈리고, 일치 부분은 유저에게 묻지 않는다.

<!-- handoff:learnings:begin -->
## Session Learnings (auto-updated by handoff)

### Implicit Rules
- Exactly 2 subagent calls per skill, one round, main thread judges (no custom agent definitions, no auto-chaining clarify→audit)
- Windows 10, PowerShell primary, Git Bash available, no jq (use PowerShell ConvertFrom-Json/ConvertTo-Json)
- Use python not python3. Node at C:\Program Files\nodejs\node.exe
- Git user Ethualo / mrleek32@gmail.com
- Session runs caveman mode (terse Korean replies) + ponytail mode (laziest working solution) via SessionStart hooks
- Two fact-forcing gates intercept first Bash call, file creation, destructive commands
- Korean prose throughout docs/skills; frontmatter keys, JSON keys, tool names, severity tags (BLOCK/WARN/NOTE) stay in original form
- Hook command uses ${CLAUDE_PLUGIN_ROOT} interpolation by Claude Code into command string, passed as argv (not environment variable read inside script)
- Patch version bumped in plugin.json when SKILL.md body changes

### Key Decisions
- Decision: Subagents perform static verification only (JSON parse, frontmatter, cross-file string identity, hook command standalone run) → Reason: Cannot restart host or invoke uninstalled plugin skill; live verification 1–3 deferred to user
- Decision: Batch all 4 plan tasks into ONE implementer dispatch → Reason: Plan held complete final text of all files, file sets disjoint, pure transcription
- Decision: Feature branch instead of git worktree → Reason: Fresh single-purpose repo, no other work in flight
- Decision: Fixed Critical + 3 Important + 2 Minors; SKIPPED Minor requesting context-budget line → Reason: Spec section 9 deliberately open pending real scenario runs; hardcoding now would fossilize baseless value
- Decision: Sonnet not haiku for transcription → Reason: Nested code fences (5-backtick containing 4-backtick containing 3-backtick) + exact-match Korean strings

<!-- handoff:learnings:end -->
