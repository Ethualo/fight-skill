# fight 플러그인 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 컨텍스트가 격리된 두 서브에이전트로 유저 지시를 적대적으로 검증하고(`fight-audit`), 모호한 지시를 양극단 두 해석으로 벌려 구체화하는(`fight-clarify`) Claude Code 플러그인을 만든다.

**Architecture:** 실행 코드가 없는 프로토콜 플러그인이다. 두 개의 SKILL.md가 `Agent` 툴 호출 절차와 역할별 프롬프트 템플릿을 담고, 판정은 메인 스레드가 한다. `SessionStart` 훅이 `AskUserQuestion` 진입 규칙을 세션당 1회 주입한다.

**Tech Stack:** Claude Code 플러그인 규격(`.claude-plugin/plugin.json`, `skills/*/SKILL.md`, `hooks/hooks.json`), Node.js(훅 실행에만 사용)

**Spec:** `docs/superpowers/specs/2026-08-27-fight-plugin-design.md`

## Global Constraints

- 서브에이전트 호출은 스킬당 정확히 2회. 1라운드 고정, 재반박 라운드 없음.
- 판정은 메인 스레드가 한다. 제3의 심판 서브에이전트를 만들지 않는다.
- 커스텀 에이전트 정의 파일(`agents/*.md`)을 만들지 않는다. 역할 프롬프트는 SKILL.md 안에 인라인 템플릿으로 둔다.
- `Agent` 툴의 `subagent_type`은 `general-purpose`를 쓴다.
- `fight-clarify` 종료 후 `fight-audit`을 자동 호출하지 않는다.
- 플러그인 루트는 리포지터리 루트다. 하위 디렉터리로 감싸지 않는다.
- 파일 인코딩은 UTF-8. BOM 없음.
- 버전은 `0.1.0`에서 시작한다.
- 문서와 스킬 본문은 한국어로 쓴다. 프런트매터 키, JSON 키, 툴 이름, 심각도 태그(`BLOCK`/`WARN`/`NOTE`)는 원문 그대로 둔다.

---

### Task 1: 플러그인 뼈대와 `fight-audit` 스킬

플러그인 매니페스트와 첫 스킬을 함께 만든다. 매니페스트 단독으로는 검증할 대상이 없으므로 한 태스크로 묶는다.

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `skills/fight-audit/SKILL.md`

**Interfaces:**
- Consumes: 없음
- Produces: 스킬 이름 `fight-audit`. `fight-clarify`의 SKILL.md가 "자동 호출하지 않는다" 문구에서 이 이름을 참조한다. 심각도 태그 `BLOCK` / `WARN` / `NOTE` / `통과`, 가정 태그 `[가정:근거]` / `[가정:공백]`.

- [ ] **Step 1: 플러그인 매니페스트 작성**

`.claude-plugin/plugin.json`:

```json
{
  "name": "fight",
  "description": "적대적 검증 — 컨텍스트가 격리된 두 서브에이전트로 유저 지시를 검증하고 모호한 지시를 구체화한다",
  "version": "0.1.0"
}
```

- [ ] **Step 2: `fight-audit` 스킬 작성**

`skills/fight-audit/SKILL.md`:

`````markdown
---
name: fight-audit
description: 유저 지시나 제안을 컨텍스트가 격리된 두 서브에이전트(제안자·감사자)로 적대적 검증한다. 동조 없는 비판, 대안 탐색, 리스크·비용 감사가 필요할 때 쓴다. 아키텍처 선택, 구현 방향 결정, 리팩터링 범위, 의존성 추가처럼 되돌리기 비용이 큰 판단이 대상이다. 오타 수정, 포매팅, 단순 편집처럼 트레이드오프가 없는 작업에는 쓰지 말 것.
---

# fight-audit

두 서브에이전트로 유저 지시를 적대적으로 검증한다. **순차** 2회 호출. 판정은 메인 스레드가 한다.

감사자가 제안자의 안을 봐야 검증이 성립하므로 병렬로 돌리지 않는다.

## 1단계 — 제안자 호출

`Agent` 툴, `subagent_type: general-purpose`, `run_in_background: false`.

프롬프트 템플릿. 중괄호 부분을 채워 쓴다.

````
너는 제안자다. 아래 지시를 구현할 구체안을 낸다.

## 지시
{유저 지시 원문 그대로. 요약하지 말 것}

## 컨텍스트
{관련 파일 경로와 핵심 코드. 지시가 건드리는 흐름만}

## 규칙
1. 지시가 비워둔 부분은 반드시 해석을 확정한다. "상황에 따라 다름"은 금지.
2. 확정한 해석마다 태그를 붙인다.
   - `[가정:근거]` — 코드나 지시에서 읽어낸 것. 근거를 한 줄로 밝힌다.
   - `[가정:공백]` — 근거 없이 메운 것. 무엇이 없어서 메웠는지 밝힌다.
3. 구현안은 어느 파일을 어떻게 바꾸는지까지 내려간다.

## 출력 형식
### 안
{구현안}

### 가정
- `[가정:근거]` {내용} — 근거: {한 줄}
- `[가정:공백]` {내용} — 없는 정보: {한 줄}
````

**제안자에게 주지 않는 것**: 네가 이미 낸 의견, 유저가 어느 쪽을 선호하는지에 대한 인상. 앵커링 제거가 이 호출의 목적이다.

## 2단계 — 감사자 호출

제안자 결과를 받은 뒤 호출한다.

````
너는 감사자다. 탐색은 최대한, 보고는 증거가 있는 것만.

## 유저 지시
{원문}

## 제안자의 안
{1단계 출력 전체}

## 순서
먼저 유저 지시 자체를 검증하고, 그 다음 제안자의 안을 검증한다.
제안자가 세운 프레임 안에 갇히지 마라.

## 공격 축 — 여섯 개 모두 필수. 하나도 건너뛸 수 없다.
| 축 | 검증 |
|---|---|
| 전제 | 지시가 참이라 가정한 사실이 실제로 참인가. 코드를 열어 확인한다 |
| 문제 정의 | 이것이 진짜 문제인가, 증상만 건드리는가 |
| 대안 | 더 적은 비용으로 같은 목표에 도달하는 길이 있는가 |
| 비용 | 유지보수·성능·복잡도 대가 |
| 실패 모드 | 엣지케이스, 에러 경로, 동시성 |
| 되돌리기 | 틀렸을 때 원복 비용 |

## 보고 규칙
- 축마다 판정을 낸다. 판정은 `BLOCK` / `WARN` / `NOTE` / `통과` 중 하나다.
- `통과`로 넘기려면 무엇을 어떻게 확인했는지 근거를 쓴다. 빈칸으로 넘기는 것은 금지다.
- 지적에는 구체적 실패 시나리오를 붙인다. 입력과 상태를 명시하고, 그 결과 무엇이 잘못되는지 쓴다.
- 실패 시나리오를 쓰지 못하는 지적은 폐기한다. 출력하지 마라.
  "확장성이 우려된다", "유지보수가 어려워질 수 있다" 같은 서술이 폐기 대상이다.
- 여섯 축이 모두 통과면 "이의 없음"으로 끝낸다. 억지로 지적을 만들지 마라.
  근거 여섯 줄이 곧 결과물이다.

## 출력 형식
### 축별 판정
- 전제 — {BLOCK|WARN|NOTE|통과}: {지적 또는 확인 근거}
  - 실패 시나리오: {입력·상태} → {잘못된 결과}      ← 지적일 때만
- 문제 정의 — {판정}: {...}
- 대안 — {판정}: {...}
- 비용 — {판정}: {...}
- 실패 모드 — {판정}: {...}
- 되돌리기 — {판정}: {...}

### 종합
{`이의 없음` 또는 가장 심각한 지적 요약}
````

## 3단계 — 메인 판정

1. 제안자와 감사자가 합의한 부분은 조용히 확정한다. 유저에게 묻지 않는다.
2. 다음 두 가지만 `AskUserQuestion`으로 올린다.
   - 감사자의 `BLOCK`과 제안자의 근거가 충돌하는 지점
   - 제안자의 `[가정:공백]`
3. 올릴 것이 없으면 묻지 않고 단일 권장안만 출력한다.
4. 감사자의 `WARN`과 `NOTE`는 권장안 아래에 목록으로 남긴다. 삭제하지 않는다.

출력은 단일 권장안 하나다. "둘 다 장단점이 있다"로 끝내지 마라.
`````

- [ ] **Step 3: 플러그인이 로드되는지 확인**

Claude Code를 이 디렉터리에서 재시작하거나 플러그인을 재로드한 뒤, 스킬 목록에 `fight:fight-audit`이 뜨는지 확인한다.

Expected: 스킬 목록에 `fight-audit`이 description과 함께 나타난다.

JSON 유효성도 함께 확인한다.

```bash
node -e "console.log(JSON.parse(require('fs').readFileSync('.claude-plugin/plugin.json','utf8')).name)"
```

Expected: `fight`

- [ ] **Step 4: 시나리오 1 — 타당한 지시에 억지 반대가 안 나오는지**

`fight-audit`을 호출하고 지시로 다음을 준다.

> plugin.json의 version을 semver로 관리하고, 스킬 본문을 바꿀 때마다 patch를 올린다.

Expected:
- 감사자가 여섯 축 전부에 판정을 냈다.
- 종합이 `이의 없음`이거나 `NOTE` 수준이다.
- `BLOCK`이 있다면 구체적 실패 시나리오(입력·상태 → 잘못된 결과)가 붙어 있다.
- "확장성이 우려된다" 류의 근거 없는 서술이 없다.

Fail 판정 기준: 실패 시나리오 없는 지적이 하나라도 출력되면 감사자 프롬프트의 보고 규칙을 강화하고 다시 돌린다.

- [ ] **Step 5: 시나리오 2 — 결함 있는 지시에 BLOCK이 나오는지**

`fight-audit`을 호출하고 지시로 다음을 준다.

> SKILL.md 두 개의 본문을 전부 plugin.json 안에 문자열로 인라인해서 파일 개수를 줄이자.

Expected:
- 최소 하나의 `BLOCK`이 나온다.
- 그 `BLOCK`에 구체적 실패 시나리오가 붙어 있다.
- `전제` 또는 `문제 정의` 축에서 지시 자체를 문제 삼는다. 제안자 안만 지적하고 끝나면 안 된다.

- [ ] **Step 6: 커밋**

```bash
git add .claude-plugin/plugin.json skills/fight-audit/SKILL.md
git commit -m "feat: fight-audit 스킬과 플러그인 매니페스트 추가"
```

---

### Task 2: `fight-clarify` 스킬

**Files:**
- Create: `skills/fight-clarify/SKILL.md`

**Interfaces:**
- Consumes: Task 1의 플러그인 매니페스트. 스킬 이름 `fight-audit`(자동 호출 금지 문구에서 참조).
- Produces: 스킬 이름 `fight-clarify`. Task 3의 훅 규칙이 이 이름으로 스킬을 지목한다. 가정 태그 `[가정]`.

- [ ] **Step 1: `fight-clarify` 스킬 작성**

`skills/fight-clarify/SKILL.md`:

`````markdown
---
name: fight-clarify
description: 모호한 지시를 양극단 두 해석으로 벌려 병렬 구현안을 만들고, 두 안이 갈리는 지점을 명세 공백으로 드러낸다. 유저가 원하는 바를 아직 언어화하지 못했을 때, 지시가 여러 해석을 허용할 때 쓴다. AskUserQuestion에서 "모르겠음 — 양극단 두 안 보여줘"가 선택되면 이 스킬을 호출한다.
---

# fight-clarify

모호한 지시를 양극단 두 해석으로 벌려 명세 공백을 드러낸다. **병렬** 2회 호출.

목적이 반박이 아니라 해석 공간을 벌리는 것이므로 두 에이전트는 서로 검증하지 않는다.

## 1단계 — 애매함 축 선정

지시에서 가장 큰 애매함 축 하나를 뽑고 양극단을 정한다.

```
"로그인 개선해줘"   축=범위   A=최소(기존 폼 UX만)      B=최대(인증 방식 재설계)
"캐시 추가해줘"     축=계층   A=앱 레벨 메모이제이션     B=인프라 레벨 Redis
"에러 처리 좀 해줘" 축=대상   A=사용자 노출 메시지만     B=내부 복구·재시도까지
```

축은 **하나만** 고른다. 두 개 이상 벌리면 두 안의 차이가 어느 축에서 왔는지 읽을 수 없다.

`AskUserQuestion`에서 "모르겠음 — 양극단 두 안 보여줘"로 진입한 경우 이 단계를 건너뛴다. 네가 물으려던 질문이 곧 애매함 축이고, 그 선택지의 양끝이 극단이다.

## 2단계 — 병렬 dispatch

`Agent` 툴 2회를 **같은 메시지에서** 호출한다. 순차로 돌리지 마라.

`subagent_type: general-purpose`, `run_in_background: false`.

각 프롬프트 템플릿. 방향만 바꿔 두 번 쓴다.

````
너는 해석자다. 아래 지시를 지정된 방향으로 해석해 구체안을 낸다.

## 지시
{유저 지시 원문 그대로}

## 배정된 해석
축: {축 이름}
방향: {극단 A 또는 극단 B의 서술}

이 방향으로 해석을 확정한다. 중간을 취하거나 다른 방향을 제안하지 마라.
배정이 과하다고 느껴져도 그 방향으로 끝까지 간다. 극단을 실물로 보는 것이 목적이다.

## 컨텍스트
{관련 파일 경로와 핵심 코드}

## 규칙
- 배정된 축 밖의 애매함은 `[가정]` 태그를 붙이고 네 판단으로 메운다.
- 구현안은 어느 파일을 어떻게 바꾸는지까지 내려간다.
- 이 해석의 대가가 무엇인지 한 줄로 밝힌다.

## 출력 형식
### 안
{구현안}

### 가정
- `[가정]` {내용}

### 이 해석의 대가
{한 줄}
````

## 3단계 — 메인 비교

1. **두 안이 일치하는 부분**은 지시가 실제로 명확했던 지점이다. 조용히 확정하고 묻지 않는다. 질문 공세를 막는 장치다.
2. **갈린 부분**이 명세 공백이다. `AskUserQuestion`으로 올린다. 선택지는 추상적 서술이 아니라 두 안의 실물 차이로 쓴다.
3. 유저 선택 후 확정된 지시문을 재작성해 출력한다. 거기서 스킬을 끝낸다.
4. `fight-audit`을 자동으로 이어 호출하지 않는다. 필요하면 유저가 부른다.

**두 안이 비슷하게 나온 경우**: 축을 잘못 뽑은 것이다. 다른 축으로 재시도하지 말고 유저에게 직접 묻는다. 재시도는 호출 비용만 두 배로 만든다.
`````

- [ ] **Step 2: 스킬이 로드되는지 확인**

플러그인 재로드 후 스킬 목록에 `fight:fight-clarify`가 뜨는지 확인한다.

Expected: `fight-audit`, `fight-clarify` 둘 다 목록에 있다.

- [ ] **Step 3: 시나리오 3 — 모호한 지시에서 두 안이 실제로 갈리는지**

`fight-clarify`를 호출하고 지시로 다음을 준다.

> fight 플러그인 문서 정리해줘.

Expected:
- 메인이 축 하나를 뽑고 양극단을 명시했다(예: 축=범위, A=기존 스펙 다듬기, B=README·사용예제·기여 가이드 신설).
- 두 `Agent` 호출이 **같은 메시지에서** 나갔다.
- 두 안의 내용이 실제로 다르다.
- 일치하는 부분은 유저에게 묻지 않았다.
- `AskUserQuestion` 선택지가 추상어("범위를 넓게"/"좁게")가 아니라 실물 차이("README만 신설"/"README + 사용예제 + 기여 가이드")로 쓰였다.

Fail 판정 기준: 두 안이 거의 같으면 1단계 축 선정 지침을 구체화한다.

- [ ] **Step 4: 커밋**

```bash
git add skills/fight-clarify/SKILL.md
git commit -m "feat: fight-clarify 스킬 추가"
```

---

### Task 3: `SessionStart` 훅

`AskUserQuestion` 진입 규칙을 세션당 1회 주입한다.

**Files:**
- Create: `hooks/askuserquestion-rule.md`
- Create: `hooks/hooks.json`

**Interfaces:**
- Consumes: 스킬 이름 `fight-clarify` (Task 2).
- Produces: 없음. 다른 태스크가 이 산출물을 참조하지 않는다.

- [ ] **Step 1: 주입할 규칙 작성**

`hooks/askuserquestion-rule.md`:

```markdown
AskUserQuestion 호출 시, 유저가 답을 모를 수 있는 설계·해석 질문이면 마지막 옵션으로 다음을 추가한다.

  label: "모르겠음 — 양극단 두 안 보여줘"
  description: "두 서브에이전트가 양극단으로 해석한 구현안을 만들어 실물로 비교한다"

이 옵션이 선택되면 fight-clarify 스킬을 호출하고, 방금 던진 질문을 애매함 축으로,
선택지의 양끝을 극단으로 쓴다. 축 선정 단계는 건너뛴다.

다음 경우에는 이 옵션을 붙이지 않는다.
- 사실 확인 질문
- 유저만 아는 정보를 묻는 질문(선호, 일정, 외부 제약)
- 선택지가 서로 실물로 구현해 볼 대상이 아닌 질문
```

- [ ] **Step 2: 훅 매니페스트 작성**

`hooks/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node -e \"process.stdout.write(require('fs').readFileSync(process.env.CLAUDE_PLUGIN_ROOT+'/hooks/askuserquestion-rule.md','utf8'))\""
          }
        ]
      }
    ]
  }
}
```

`node`를 쓰는 이유: `cat`은 Windows `cmd`에 없고, `echo`로 여러 줄 UTF-8을 내보내면 인코딩이 깨진다. `node`는 두 문제를 모두 피한다. 대신 Node.js 의존이 생기며, 이는 Task 4의 CLAUDE.md에 기록한다.

- [ ] **Step 3: 훅 명령이 단독으로 동작하는지 확인**

```bash
CLAUDE_PLUGIN_ROOT=. node -e "process.stdout.write(require('fs').readFileSync(process.env.CLAUDE_PLUGIN_ROOT+'/hooks/askuserquestion-rule.md','utf8'))"
```

Expected: 규칙 전문이 한글 깨짐 없이 그대로 출력된다.

JSON 유효성도 확인한다.

```bash
node -e "JSON.parse(require('fs').readFileSync('hooks/hooks.json','utf8')); console.log('ok')"
```

Expected: `ok`

- [ ] **Step 4: 새 세션에서 규칙이 주입되는지 확인**

Claude Code를 새로 시작한다.

Expected: 세션 시작 컨텍스트에 `SessionStart` 훅 출력으로 규칙 전문이 나타난다. 한글이 깨지지 않는다.

Fail 시: `process.env.CLAUDE_PLUGIN_ROOT`가 비어 있으면 훅 실행 컨텍스트에서 그 변수가 제공되지 않는 것이다. 상대 경로 `./hooks/askuserquestion-rule.md`로 바꿔 재시도하고, 어느 쪽이 동작했는지 기록한다.

- [ ] **Step 5: 옵션이 실제로 붙는지 확인**

새 세션에서 모호한 요청을 준다.

> 이 플러그인에 로깅 좀 넣어줘.

Expected: Claude가 `AskUserQuestion`을 띄우고, 마지막 선택지로 "모르겠음 — 양극단 두 안 보여줘"가 있다. 그것을 고르면 `fight-clarify`가 호출되고 축 선정 단계를 건너뛴다.

- [ ] **Step 6: 커밋**

```bash
git add hooks/askuserquestion-rule.md hooks/hooks.json
git commit -m "feat: AskUserQuestion 진입 규칙을 주입하는 SessionStart 훅 추가"
```

---

### Task 4: 프로젝트 CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

**Interfaces:**
- Consumes: Task 1–3의 최종 파일 구조와 Node.js 의존.
- Produces: 없음.

- [ ] **Step 1: CLAUDE.md 작성**

앞선 태스크에서 확정된 내용만 쓴다. Task 3 Step 4에서 상대 경로로 폴백했다면 그 사실을 반영한다.

`CLAUDE.md`:

```markdown
# fight

적대적 검증 Claude Code 플러그인. 실행 코드 없음. 프로토콜 문서와 훅만 있다.

## 구조

| 경로 | 역할 |
|---|---|
| `.claude-plugin/plugin.json` | 플러그인 매니페스트 |
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
- **훅은 Node.js에 의존한다.** `cat`은 Windows `cmd`에 없고 `echo`는 UTF-8 여러 줄을 깨뜨려서 `node`를 쓴다.
- 스킬 본문을 고치면 `plugin.json`의 patch 버전을 올린다.

## 검증

단위 테스트가 없다. 실행 로직이 없기 때문이다. 검증은 실제 호출로 한다.
계획 문서의 시나리오 1–3을 그대로 다시 돌린다.

1. 타당한 지시 → 감사자가 "이의 없음"과 근거 여섯 줄을 반환한다.
2. 결함 있는 지시 → 구체적 실패 시나리오와 함께 `BLOCK`이 나온다.
3. 모호한 지시 → 두 안이 실제로 갈리고, 일치 부분은 유저에게 묻지 않는다.
```

- [ ] **Step 2: 커밋**

```bash
git add CLAUDE.md
git commit -m "docs: 프로젝트 CLAUDE.md 추가"
```

---

## 완료 후 남는 것

스펙 9절 미결 사항 중 이 계획이 확정한 것과 남는 것.

**확정됨**
- 스킬 이름: `fight-audit`, `fight-clarify`
- 슬래시 커맨드: 별도로 만들지 않는다. 스킬 이름이 곧 호출 경로다(`/fight-audit`).
- 제안자 컨텍스트: 직접 대상·계약/설정·호출자/소비자/테스트 순서로 수집하며, 최대 8개 파일·24,576 UTF-8 bytes. S1 5개/18,531 bytes, S2 6개/23,142 bytes 실측.
- 공개 문서: `README.md`, `readme.ko.md`, `CONTRIBUTING.md`, `LICENSE`가 `7e2d954`에 추가됨.

**남음**
- 마켓플레이스 공개·등록 여부. 사용자가 보류한 상태라 다루지 않는다.
