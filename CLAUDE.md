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

`fight-clarify`의 두 서브에이전트는 서로 검증하지 않는다. 목적이 반박이 아니라 해석 공간을 벌리는 것이기 때문이다.

## 모델 정책

| 플랫폼 | `fight-audit` | `fight-clarify` |
|---|---|---|
| Claude Code | 제안자 `sonnet`, 감사자 `opus` | 두 호출 모두 `sonnet` 고정 |

Codex 모델·reasoning·`fork_context`·fallback 정책은 [AGENTS.md](AGENTS.md)의 환경과 주요 패턴을 기준으로 한다. 표의 모델은 스킬이 요청하는 값이며, 매니페스트가 모델 가용성·대체 여부를 강제하지는 않는다.

두 플랫폼 모두 외부 provider·CLI·MCP를 사용하지 않는다. Claude Code와 Codex 호스트가 요청 모델을 쓸 수 없거나 대체하면 메인 에이전트가 이를 밝히고 호출을 중단해야 한다. 이 규칙은 호스트 준수에 의존한다.

## 주의사항

- **서브에이전트 호출은 스킬당 정확히 2회라는 프로토콜이다.** 호스트가 따르도록 지시하지만 플러그인 파일이 계수·강제하지는 않는다.
- **판정은 메인 스레드가 한다.** 심판 서브에이전트를 추가하지 마라. 메인만 대화 히스토리와 코드베이스 컨텍스트를 가진다.
- **감사자의 보고 규칙을 완화하지 마라.** 실패 시나리오를 요구하는 조항이 억지 반대를 막는 유일한 장치다.
- **감사자에게 "이의 없음"을 허용해야 한다.** 매번 무언가를 내라고 강제하면 그 자체가 억지 반대다.
- **`fight-clarify`는 축을 하나만 고른다.** 두 개 이상 벌리면 두 안의 차이를 읽을 수 없다.
- **훅은 Node.js에 의존한다.** `cat`은 Windows `cmd`에 없고 `echo`는 UTF-8 여러 줄을 깨뜨려서 `node`를 쓴다. 플러그인 루트 경로는 `process.env.CLAUDE_PLUGIN_ROOT`로 읽지 않고 `${CLAUDE_PLUGIN_ROOT}`를 커맨드 문자열에 그대로 넣어 `argv`로 넘긴다. Claude Code가 셸에 넘기기 전에 문자열 치환을 하므로 환경변수 미설정에 영향받지 않는다.
- 스킬 본문을 고치면 `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` 세 버전의 patch를 함께 올린다.
- 버전을 올릴 때는 `CHANGELOG.md`에도 해당 버전 항목을 남긴다.

## 검증

릴리스 일치는 `python -X utf8 scripts/check_release.py`로 검사한다. 스킬의 행동과 호출 순서 검증은 실제 호출로 한다.
계획 문서의 시나리오 1–3을 그대로 다시 돌린다.

아래 표는 기존 검증 기록이다. 0.3.10의 판정 규칙 검사와 전체 라이브 검증의 구분은 [회귀 검증 기록](docs/verification/0.3.10.md)을, 0.3.11 재시작 후 재실행 결과는 [0.3.11 라이브 검증](docs/verification/0.3.11.md)을 참고한다.

| 시나리오 | 내용 | Claude Code | Codex |
|---|---|---|---|
| 1 | 타당한 지시 → 감사자가 "이의 없음"과 근거 여섯 줄을 반환한다 | 통과(0.3.6) / 0.3.11 재실행에서는 제안자의 인용 조작·범위 오판을 감사자가 NOTE 2건으로 잡아 `이의 없음` 아님 — [상세](docs/verification/0.3.11.md) | 기대값 미충족 — 제안안 결함으로 유효한 `BLOCK` 발생 |
| 2 | 결함 있는 지시 → 구체적 실패 시나리오와 함께 `BLOCK`이 나온다 | 통과 | 통과 |
| 3 | 모호한 지시 → 두 안이 실제로 갈리고, 일치 부분은 유저에게 묻지 않는다 | 통과 | 통과 |

Codex 시나리오 1은 감사자가 여섯 축·근거·실패 시나리오를 모두 출력했지만, 제안안의 결함 때문에 `이의 없음`이 아니라 유효한 `BLOCK`으로 끝났다. 시나리오 2와 3은 기대 결과를 확인했다. Claude Code 시나리오 1도 0.3.11 재실행에서 같은 패턴(지시는 타당해도 제안자 출력에 실결함이 있으면 통과시키지 않음)을 보였다 — 감사자가 매번 "이의 없음"을 자동 반환하지 않는다는 증거다.

### Codex 감사자 effort 비교 시나리오

`gpt-5.6-sol` 감사자의 기본 effort를 `low`로 바꿀지 결정할 때만 아래 시나리오를 쓴다. 각 실행은 같은 기준 커밋과 같은 유저 지시·제안자 출력·관련 파일 발췌를 사용한다. 제안자 출력은 고정해 감사자 effort만 변수가 되게 한다.

| 시나리오 | 고정 제안 | 기대 판정 | 필수 근거 |
|---|---|---|---|
| 4 — 모델 핀 제거 | `fight-audit`의 Claude `opus` 및 Codex `sol` 모델 지정을 삭제하고 부모 세션을 상속한다 | `BLOCK` | `skills/fight-audit/SKILL.md`의 명시 모델 계약과 상속 시 감사자 열화 경로 |
| 5 — 불완전 배포 | `SKILL.md`를 수정하면서 한 플랫폼 매니페스트 또는 `.agents/plugins/marketplace.json`의 버전은 올리지 않는다 | `BLOCK` | 양 플랫폼 버전 규칙과 버전별 설치 캐시가 이전 본문을 계속 실행하는 경로 |
| 6 — 컨텍스트 상한 위반 | 제안자에게 전체 저장소·git 이력·handoff를 넘기고 8개 파일/24,576-byte 상한을 없앤다 | `BLOCK` | `AGENTS.md`의 컨텍스트 예산과 큰 문서 묶음에서 비용·앵커링이 커지는 경로 |
| 7v2 — 정상 문서 보강(비중복) | `CLAUDE.md`와 `AGENTS.md`에 "`fight-clarify`의 두 서브에이전트는 서로 검증하지 않는다"(`skills/fight-clarify/SKILL.md:10`) 한 문장을 각각 추가한다. 스킬·매니페스트·모델·설치는 건드리지 않는다 | `이의 없음` | 두 README 어디에도 이 문장이 없어 신규 보강이며, 문서 추가만으로 런타임이 바뀌지 않는다는 확인 |
| 8v2 — 정상 스킬 문구 보강(정확 교체+배포 경계) | `skills/fight-clarify/SKILL.md:83`의 "두 안이 일치하는 부분은 지시가 실제로 명확했던 지점이다. 조용히 확정하고 묻지 않는다. 질문 공세를 막는 장치다."를 "두 안이 일치하는 부분은 지시가 실제로 명확했던 지점이므로 갈린 부분만 질문으로 올린다. 일치 부분을 다시 묻는 질문 공세를 막는 장치다."로 교체(의미 동일, 문구만 명확화)한다. 동시에 `.claude-plugin/plugin.json`·`.codex-plugin/plugin.json`·`.agents/plugins/marketplace.json` 세 버전을 `0.3.8`로 함께 올리고, `AGENTS.md`의 세 정적 검증 명령을 모두 실행한다. `0.3.8` 배포 후 Claude Code marketplace를 갱신하고 `claude plugin update fight@fight`와 재시작으로 설치본을 갱신한 뒤 Codex와 Claude Code에서 두 스킬을 각각 실제 호출해 subagent 수·순서·출력과 clarify가 공통점을 다시 묻지 않음을 확인한다. 배포 뒤 회귀가 확인되면 문장과 세 버전을 `0.3.9`로 함께 되돌려 같은 정적 검증을 다시 실행·배포하고, Claude Code marketplace·설치본을 갱신·재시작한 뒤 같은 라이브 검증을 다시 실행한다. "저장소 편집은 즉시 반영되지만 설치된 Claude Code 플러그인(`~/.claude/plugins/cache/fight/fight/{version}/`)은 `claude plugin update fight@fight` 실행과 재시작 전까지 이전 본문을 계속 실행한다"는 배포 경계를 PR 설명에 명시한다 | `이의 없음` 또는 비차단 `NOTE` | 교체 문구가 원문과 의미 동일함, 세 배포 표면 버전 동시 갱신과 정적·라이브 검증, 저장소·설치본 경계와 다음 patch 롤백 절차 명시로 v1(S8)의 모호했던 교체 범위·설치 완료 기준이 해소됐다는 확인 |

> S7/S8 v2는 `.handoff` 검증(2026-09-02)에서 v1이 각각 "기존 README 계약과 중복"·"교체 문구·설치 범위 미명시"로 판정이 갈렸던 문제를 고치기 위해 재정의했다. v1 행은 기록 보존을 위해 유지하지 않고 이 표에서 교체한다.

각 시나리오를 `low`와 현재 `medium`에서 무작위 순서로 3회씩 실행한다. 매번 여섯 축 모두의 파일·줄 또는 명령 근거를 기록하고, `BLOCK`/`WARN`에는 입력·상태→잘못된 결과 형태의 실패 시나리오가 있어야 한다. 호스트가 제공하면 실행 시간과 토큰·비용도 기록하고, 제공하지 않으면 추정하지 말고 `측정 불가`로 남긴다.

`low` 채택 조건은 15회 모두 기대 판정을 만족하고, `medium`보다 누락·근거 부실·정상안 오차단이 없어야 한다. 또한 실제 측정된 비용 또는 시간이 더 낮아야 한다. 어느 하나라도 만족하지 못하거나 측정값이 없으면 `medium`을 유지한다.

#### S7v2/S8v2 재측정 결과 (2026-09-02)

기준 커밋은 `ac228ca^`이며, 제안자 안·파일 발췌는 고정했다. 최종 S8v2는 정적·라이브 검증, marketplace→plugin update→재시작 순서, 다음 patch 롤백까지 명시한 안으로 다시 고정했다.

| 시나리오 | low | medium | 결과 |
|---|---:|---:|---|
| 7v2 | 3/3 `이의 없음` | 3/3 `이의 없음` | 기대 판정 충족 |
| 8v2 | 3/3 `이의 없음` | 3/3 `이의 없음` | 기대 판정 충족 |

호스트는 서브에이전트별 토큰·비용·대기열 포함 시간을 제공하지 않아 모두 `측정 불가`다. 이 재측정은 S7v2/S8v2 여섯 조건만 덮으므로 15회 채택 조건을 충족하지 않으며, 비용·시간 우위도 입증되지 않았다. 기본 effort는 `medium`을 유지한다.

#### S4–S6 실측 결과 (2026-09-03)

기준 커밋은 `ac228ca^`이며, 각 시나리오의 Terra `xhigh` 제안자 출력은 1회 생성 후 고정했다. 감사자는 `gpt-5.6-sol`, `fork_context: false`로 두고 `low`·`medium`을 각 3회씩 무작위 순서로 실행했다. 실행 순서는 `S4-M-1, S5-L-1, S6-M-1` → `S4-L-1, S5-M-1, S6-L-1` → `S4-M-2, S5-L-2, S6-M-2` → `S4-L-2, S5-M-2, S6-L-2` → `S4-L-3, S5-L-3, S6-M-3` → `S4-M-3, S5-M-3, S6-L-3`이다.

축 코드는 `전제/문제 정의/대안/비용/실패 모드/되돌리기` 순서이며, 모든 실행이 여섯 축과 종합 판정을 출력했다. `BLOCK`·`WARN` 지적에는 입력·상태→잘못된 결과 실패 시나리오가 포함됐다.

| 실행 | effort | 축별 판정 | 종합 |
|---|---|---|---|
| S4-L-1 | low | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |
| S4-L-2 | low | WARN/BLOCK/BLOCK/WARN/WARN/통과 | BLOCK |
| S4-L-3 | low | BLOCK/BLOCK/통과/BLOCK/WARN/WARN | BLOCK |
| S4-M-1 | medium | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |
| S4-M-2 | medium | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |
| S4-M-3 | medium | WARN/BLOCK/통과/WARN/WARN/BLOCK | BLOCK |
| S5-L-1 | low | BLOCK/BLOCK/WARN/WARN/BLOCK/WARN | BLOCK |
| S5-L-2 | low | BLOCK/BLOCK/BLOCK/WARN/BLOCK/통과 | BLOCK |
| S5-L-3 | low | BLOCK/WARN/BLOCK/WARN/BLOCK/통과 | BLOCK |
| S5-M-1 | medium | BLOCK/BLOCK/WARN/WARN/BLOCK/WARN | BLOCK |
| S5-M-2 | medium | BLOCK/BLOCK/WARN/WARN/BLOCK/통과 | BLOCK |
| S5-M-3 | medium | BLOCK/WARN/BLOCK/WARN/BLOCK/통과 | BLOCK |
| S6-L-1 | low | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |
| S6-L-2 | low | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |
| S6-L-3 | low | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |
| S6-M-1 | medium | BLOCK/BLOCK/WARN/BLOCK/BLOCK/BLOCK | BLOCK |
| S6-M-2 | medium | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |
| S6-M-3 | medium | BLOCK/BLOCK/WARN/BLOCK/BLOCK/WARN | BLOCK |

공통 근거 앵커는 S4의 `skills/fight-audit/SKILL.md:71,73` 및 `AGENTS.md:34-35,60-63`, S5의 `skills/fight-audit/SKILL.md:99-105` 및 세 매니페스트 버전 필드·`AGENTS.md:61-63`, S6의 `skills/fight-audit/SKILL.md:20-29`, `AGENTS.md:48-55`, `git ls-tree -r -l ac228ca^`, `git rev-list --count ac228ca^`다.

S4–S6은 `low`·`medium` 모두 9/9 `BLOCK`으로 기대 판정을 충족했다. 위 S7v2/S8v2 결과까지 합치면 `low` 15/15, `medium` 15/15로 판정은 동일하다. 그러나 호스트가 서브에이전트별 토큰·비용·대기열 포함 시간을 제공하지 않아 비용·시간 우위는 측정 불가하며, 일부 실행은 기준 발췌가 아닌 후속 문서도 근거로 인용했다. 따라서 품질 동등성을 확인했다는 수준에서 멈추고, `low`로 변경하지 않으며 기본 effort는 `medium`을 유지한다.

<!-- handoff:learnings:begin -->
## Session Learnings (auto-updated by handoff)

### Implicit Rules
- fight 마켓플레이스는 GitHub git remote(origin/master, https://github.com/Ethualo/fight-skill.git) 추적, 로컬 체크아웃 경로 아님 — 로컬 편집만으론 claude plugin marketplace update/plugin update가 반영 안됨, 반드시 push 필요.
- claude plugin marketplace update <name>과 claude plugin update <name>@<name> 명령은 non-interactive Bash로 실행 가능, 단 적용은 재시작 후.

### Key Decisions
- 유저결정: 라이브검증 위해 '커밋 후 master에 푸시' 선택 — 이유: 설치된 fight 마켓플레이스가 git remote(origin/master) 추적이라 로컬 uncommitted 변경으론 반영 안됨. AskUserQuestion 3지선다(푸시/임시 로컬 마켓플레이스/정적검증만) 중 정식 배포 경로 택함.
- 메인결정: 감사자 BLOCK 해결 위해 태그 기본값을 [대상:제안안]에서 [대상:지시]로 반전, '구현대안 채택만으로 해결' 문구 삭제 — 이유: 원안 기본값이 지시 자체 결함을 제안안 교체로 조용히 확정시켜 SKILL.md 85행 '지시 먼저 검증' 원칙을 무력화하는 실패경로 존재.
- 메인결정: fight-clarify 상한 절을 fight-audit 참조 한 줄로 작성, 숫자(8개/24576bytes) 재복제 안함 — 이유: 감사자 지적대로 숫자가 이미 5곳에 있어 6번째 복제 시 향후 상한 변경 때 누락 위험 존재.

<!-- handoff:learnings:end -->
