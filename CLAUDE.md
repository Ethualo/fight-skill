# fight

적대적 검증 플러그인. Claude Code와 Codex 양쪽에서 공통 프로토콜 본문을 공유하지만 호출 문법·도구·훅·모델 해석은 다르다. 서브에이전트 오케스트레이터는 없고, Claude Code 전용 Node.js SessionStart 훅만 규칙을 주입한다.

Codex 유지보수·모델·검증 명령은 [AGENTS.md](AGENTS.md)를 참고한다. 스킬 본문(`skills/*/SKILL.md`)은 두 플랫폼이 공유하며, 호출 계약(서브에이전트 스폰 방식)만 플랫폼별로 분기한다.

## 설치 (Claude Code)

```
/plugin marketplace add Ethualo/fight-skill
/plugin install fight@fight
```

로컬 체크아웃에서는 첫 명령에 로컬 클론 경로를 쓴다. 갱신은 `/plugin marketplace update fight` → `/plugin update fight@fight` → `/reload-plugins` 또는 재시작 순서다.

## 구조

| 경로 | 역할 |
|---|---|
| `.claude-plugin/plugin.json` | Claude Code 플러그인 매니페스트 |
| `.claude-plugin/marketplace.json` | 마켓플레이스 매니페스트. 설치 진입점 |
| `.codex-plugin/plugin.json` | Codex 플러그인 매니페스트 |
| `.agents/plugins/marketplace.json` | Codex repo marketplace. 저장소 루트 플러그인을 노출 |
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

Codex 모델·reasoning·`fork_context`·fallback 정책은 [AGENTS.md](AGENTS.md)의 환경과 주요 패턴을 기준으로 한다. 표의 모델은 스킬이 요청하는 값이며, 매니페스트가 모델 가용성·대체 여부를 강제하지는 않는다.

두 플랫폼 모두 외부 provider·CLI·MCP를 사용하지 않는다. Claude Code와 Codex 호스트가 요청 모델을 쓸 수 없거나 대체하면 메인 에이전트가 이를 밝히고 호출을 중단해야 한다. 이 규칙은 호스트 준수에 의존한다.

## 주의사항

- **서브에이전트 호출은 스킬당 정확히 2회라는 프로토콜이다.** 호스트가 따르도록 지시하지만 플러그인 파일이 계수·강제하지는 않는다.
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
| 1 | 타당한 지시 → 감사자가 "이의 없음"과 근거 여섯 줄을 반환한다 | 통과 | 기대값 미충족 — 제안안 결함으로 유효한 `BLOCK` 발생 |
| 2 | 결함 있는 지시 → 구체적 실패 시나리오와 함께 `BLOCK`이 나온다 | 통과 | 통과 |
| 3 | 모호한 지시 → 두 안이 실제로 갈리고, 일치 부분은 유저에게 묻지 않는다 | 통과 | 통과 |

Codex 시나리오 1은 감사자가 여섯 축·근거·실패 시나리오를 모두 출력했지만, 제안안의 결함 때문에 `이의 없음`이 아니라 유효한 `BLOCK`으로 끝났다. 시나리오 2와 3은 기대 결과를 확인했다.

### Codex 감사자 effort 비교 시나리오

`gpt-5.6-sol` 감사자의 기본 effort를 `low`로 바꿀지 결정할 때만 아래 시나리오를 쓴다. 각 실행은 같은 기준 커밋과 같은 유저 지시·제안자 출력·관련 파일 발췌를 사용한다. 제안자 출력은 고정해 감사자 effort만 변수가 되게 한다.

| 시나리오 | 고정 제안 | 기대 판정 | 필수 근거 |
|---|---|---|---|
| 4 — 모델 핀 제거 | `fight-audit`의 Claude `opus` 및 Codex `sol` 모델 지정을 삭제하고 부모 세션을 상속한다 | `BLOCK` | `skills/fight-audit/SKILL.md`의 명시 모델 계약과 상속 시 감사자 열화 경로 |
| 5 — 불완전 배포 | `SKILL.md`를 수정하면서 한 플랫폼 매니페스트 또는 `.agents/plugins/marketplace.json`의 버전은 올리지 않는다 | `BLOCK` | 양 플랫폼 버전 규칙과 버전별 설치 캐시가 이전 본문을 계속 실행하는 경로 |
| 6 — 컨텍스트 상한 위반 | 제안자에게 전체 저장소·git 이력·handoff를 넘기고 8개 파일/24,576-byte 상한을 없앤다 | `BLOCK` | `AGENTS.md`의 컨텍스트 예산과 큰 문서 묶음에서 비용·앵커링이 커지는 경로 |
| 7v2 — 정상 문서 보강(비중복) | `CLAUDE.md`와 `AGENTS.md`에 "`fight-clarify`의 두 서브에이전트는 서로 검증하지 않는다"(`skills/fight-clarify/SKILL.md:10`) 한 문장을 각각 추가한다. 스킬·매니페스트·모델·설치는 건드리지 않는다 | `이의 없음` | 두 README 어디에도 이 문장이 없어 신규 보강이며, 문서 추가만으로 런타임이 바뀌지 않는다는 확인 |
| 8v2 — 정상 스킬 문구 보강(정확 교체+배포 경계) | `skills/fight-clarify/SKILL.md:83`의 "두 안이 일치하는 부분은 지시가 실제로 명확했던 지점이다. 조용히 확정하고 묻지 않는다. 질문 공세를 막는 장치다."를 "두 안이 일치하는 부분은 지시가 실제로 명확했던 지점이므로 갈린 부분만 질문으로 올린다. 일치 부분을 다시 묻는 질문 공세를 막는 장치다."로 교체(의미 동일, 문구만 명확화)한다. 동시에 `.claude-plugin/plugin.json`·`.codex-plugin/plugin.json`·`.agents/plugins/marketplace.json` 세 버전을 patch 단위로 함께 올리고, "저장소 편집은 즉시 반영되지만 설치된 Claude Code 플러그인(`~/.claude/plugins/cache/fight/fight/{version}/`)은 `claude plugin update fight@fight` 실행과 재시작 전까지 이전 본문을 계속 실행한다"는 배포 경계를 PR 설명에 명시한다 | `이의 없음` 또는 비차단 `NOTE` | 교체 문구가 원문과 의미 동일함, 세 배포 표면 버전 동시 갱신, 저장소·설치본 경계 명시로 v1(S8)의 모호했던 교체 범위·설치 완료 기준이 해소됐다는 확인 |

> S7/S8 v2는 `.handoff` 검증(2026-09-02)에서 v1이 각각 "기존 README 계약과 중복"·"교체 문구·설치 범위 미명시"로 판정이 갈렸던 문제를 고치기 위해 재정의했다. v1 행은 기록 보존을 위해 유지하지 않고 이 표에서 교체한다.

각 시나리오를 `low`와 현재 `medium`에서 무작위 순서로 3회씩 실행한다. 매번 여섯 축 모두의 파일·줄 또는 명령 근거를 기록하고, `BLOCK`/`WARN`에는 입력·상태→잘못된 결과 형태의 실패 시나리오가 있어야 한다. 호스트가 제공하면 실행 시간과 토큰·비용도 기록하고, 제공하지 않으면 추정하지 말고 `측정 불가`로 남긴다.

`low` 채택 조건은 15회 모두 기대 판정을 만족하고, `medium`보다 누락·근거 부실·정상안 오차단이 없어야 한다. 또한 실제 측정된 비용 또는 시간이 더 낮아야 한다. 어느 하나라도 만족하지 못하거나 측정값이 없으면 `medium`을 유지한다.

<!-- handoff:learnings:begin -->
## Session Learnings (auto-updated by handoff)

### Implicit Rules
- gpt-5.6-sol is a Codex-only model; this repo's Claude Code session has no tool or CLI to invoke it directly — any effort-comparison rerun needs a literal Codex session.
- CLAUDE.md's experimental scenario section (S1-S8) is user-owned content per prior handoff; edits to it should stay scoped to fixture text, not skill/manifest/model files, unless the user asks otherwise.
- skills/fight-clarify/SKILL.md:10 states subagents don't cross-validate — this fact was not previously mirrored in either README, which is why it was chosen as the S7v2 addition.

### Key Decisions
- Decision: Draft S7v2/S8v2 fixture wording directly in CLAUDE.md rather than attempting execution — Reason: user explicitly chose the fixture-only option after being told this session has no codex CLI to invoke the gpt-5.6-sol auditor.
- Decision: S7v2 adds a new sentence (subagents don't cross-validate) instead of restating existing 순차/병렬 rules — Reason: v1 duplicated content already in AGENTS.md 주요패턴, which caused inconsistent low-effort verdicts; the new sentence is verifiably absent from both READMEs.
- Decision: S8v2 specifies the exact replacement sentence for SKILL.md:83 plus a repo-vs-installed-cache boundary statement — Reason: v1 only said 'clarify wording' vaguely, leaving replacement text and install-completion criteria to auditor interpretation, which caused the low-effort BLOCK split; AGENTS.md already defines the repo/cache distinction so S8v2 just requires stating it explicitly.
- Decision: Replace v1 rows outright rather than keep both — Reason: keeps the experimental scenario table from growing unbounded; v1 history is preserved in this handoff and the prior one, not in the live doc.

<!-- handoff:learnings:end -->
