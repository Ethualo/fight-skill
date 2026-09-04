# fight-skill 작업 지침

Codex 유지보수 지침이다. 플러그인은 Claude Code와 Codex 양쪽을 지원하며 외부 모델 provider, CLI, MCP에 의존하지 않는다.

Claude Code 설치와 공통 개요는 [CLAUDE.md](CLAUDE.md)를 참고한다. `skills/*/SKILL.md`는 두 플랫폼이 공유하는 단일 본문이며, 서브에이전트 호출 계약만 플랫폼별로 분기한다 — Codex는 subagent spawn 도구, Claude Code는 `Agent` 툴.

## 구조

- `.codex-plugin/plugin.json`: Codex 플러그인 매니페스트
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`: Claude Code 플러그인·마켓플레이스 매니페스트
- `hooks/`: Claude Code 전용 SessionStart 훅. Codex는 사용하지 않음
- `skills/fight-audit/`: 제안자·감사자 비대칭 검증 프로토콜 (양 플랫폼 공유)
- `skills/fight-clarify/`: 양극단 해석 병렬 분기 프로토콜 (양 플랫폼 공유)
- `scripts/check_release.py`: 세 매니페스트·README 버전·모델 표·변경 이력 일치 검사
- `docs/superpowers/`: 설계 스펙과 최초 Claude Code 구현 계획. 역할 구조(비대칭·대칭)의 근거는 지금도 유효하다

## 실행 및 검증

### 정적 검증

- 릴리스 일치 검사: `python -X utf8 scripts/check_release.py`
- Codex 플러그인 검증: `python C:\Users\user\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .`
- 스킬 검증: `python -X utf8 C:\Users\user\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\fight-audit`
- 스킬 검증: `python -X utf8 C:\Users\user\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\fight-clarify`

### 라이브 검증

- Codex와 Claude Code 각각에서 두 스킬을 실제 호출해 subagent 수·순서·출력을 확인한다.
- 감사자는 파일·줄 또는 명령 근거와 구체적 실패 시나리오를 남겨야 한다.
- 해석자는 같은 메시지에서 병렬 실행한다. 근거 있는 공통점은 재질문하지 않고, 근거 없는 공통 가정은 미확정으로 남긴다.

## 환경

- Windows 10, PowerShell 우선
- 외부 환경변수 없음
- Codex 모델 서열: `sol` > `terra` > `luna`. reasoning effort는 `low`/`medium`/`high`/`xhigh`/`max`/`ultra` 6단계
- Codex 서브에이전트 모델: fight-audit은 제안자 `gpt-5.6-terra`(reasoning `xhigh`) / 감사자 `gpt-5.6-sol`(reasoning `medium`, 비용 절감 실험 중 — 벤더 권장은 `max`, 실측 후 조정) 고정(감사자만 상위 모델 — 근거는 `skills/fight-audit/SKILL.md` 2단계), fight-clarify는 두 호출 모두 `gpt-5.6-luna`(reasoning `max`, 대칭 구조라 열화 리스크 없고 해석 작업 자체가 "명확한 구현" 범주)
- Claude Code 서브에이전트 모델: fight-audit은 제안자 `sonnet` / 감사자 `opus` 고정, fight-clarify는 두 호출 모두 `sonnet` 고정 — 근거는 `skills/fight-audit/SKILL.md` 2단계, `skills/fight-clarify/SKILL.md` 2단계 참고

## 주요 패턴

- 스킬당 서브에이전트 호출은 정확히 2회
- `fight-audit`은 순차 호출, `fight-clarify`는 같은 메시지에서 병렬 호출
- `fight-clarify`의 두 서브에이전트는 서로 검증하지 않는다. 목적이 반박이 아니라 해석 공간을 벌리는 것이기 때문이다
- Codex 서브에이전트는 `fork_context: false`로 메인 대화 추론을 상속하지 않음
- 판정과 사용자 질문은 메인 스레드가 담당
- 한국어 본문과 기존 태그·출력 형식을 유지

## 제안자 컨텍스트 예산

- `fight-audit` 제안자 컨텍스트는 `직접 대상 파일 → 직접 계약·설정 → 직접 호출자·소비자·테스트` 순서로 수집한다.
- 전체 저장소, git 이력, handoff, 관련 없는 역사 문서와 파일은 제외한다.
- 컨텍스트 블록은 최대 저장소 파일 8개와 선택 발췌 UTF-8 24,576 bytes다. 유저 지시 원문·고정 스킬 프롬프트·에이전트 출력은 이 한도에서 제외한다.
- 초과 시 우선순위가 낮은 파일은 경로와 생략 사유만 남긴다. 한도를 조용히 넘기지 않는다.

현재 저장소의 전체 파일을 최악의 입력으로 계산한 기준은 S1 5개/18,531 bytes, S2 6개/23,142 bytes다. 따라서 8개/24,576 bytes를 제안자 상한으로 확정했다. S3 문서 정리 묶음은 14개/86,267 bytes이므로 clarify 해석자에게 전체를 넣지 않고 경로와 필요한 발췌만 사용한다.

기존 Codex 라이브 기록의 제안자 실행량은 S1 69,109·78,813, S2 82,113 tokens였고, proposer+auditor 전체 라운드는 163,793–174,118 tokens였다. 이 수치는 실행 총량이지 입력 컨텍스트 상한이 아니므로 24,576-byte 입력 상한과 혼동하지 않는다.

## 주의사항

- 외부 provider·CLI·MCP fallback을 추가하지 않음
- 지정 모델을 사용할 수 없으면 조용히 다른 모델로 대체하지 않고 중단
- `skills/*/SKILL.md` 변경 시 `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.agents/plugins/marketplace.json` 세 버전을 함께 올리고 재검증
- 버전을 올릴 때는 `CHANGELOG.md`에도 해당 버전 항목을 남긴다
- 감사자의 근거 없는 통과나 실패 시나리오 없는 지적을 허용하지 않음
- 설치된 Claude Code 플러그인은 `~/.claude/plugins/cache/fight/fight/{version}/`의 버전별 스냅샷 복사본이다. 저장소 편집만으로는 실행 중인 내용이 바뀌지 않는다 — 버전을 올리고 `claude plugin update fight@fight`를 실행해야 반영된다

<!-- handoff:learnings:begin -->
## Session Learnings (auto-updated by handoff)

### Implicit Rules
- Repo has parallel platform support: Claude Code (.claude-plugin/) and Codex (.codex-plugin/, .agents/plugins/marketplace.json) — any skills/*/SKILL.md content change requires bumping ALL platform manifest versions together (documented rule in both CLAUDE.md and AGENTS.md '주의사항' sections).
- Static validation commands: python C:\Users\user\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py . and python -X utf8 C:\Users\user\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\<skill-name> — must run via PowerShell tool, not Bash (Bash mangles Windows backslash paths).
- Repo default branch for PRs is master; active dev branch is dev. No CI — verification is manual re-run of scenarios 1-3 from docs/superpowers/plans.
- This session's Claude Code CLI has no Codex CLI/tool access, so any Codex-model (gpt-5.6-sol/terra/luna) live verification must happen in a literal Codex session, not here.

### Key Decisions
- Decision: bump only 3 manifest files (.claude-plugin/plugin.json, .codex-plugin/plugin.json, .agents/plugins/marketplace.json) → Reason: grep-verified .claude-plugin/marketplace.json carries no version field for fight plugin, so S8v2 spec's '3 versions' maps exactly to these 3 files.
- Decision: merge dev→master via real merge commit, not fast-forward → Reason: git merge --ff-only failed since master had 3 prior sync merge commits not on dev's ancestry; diffed master-only vs dev-only commits first, confirmed no unique content in those merges, then did normal merge (clean, no conflicts).
- Decision: backfill CHANGELOG.md history for 0.1.0-0.3.8 rather than starting empty at current version → Reason: user asked generically whether changelogs work for already-far-along projects; chose backfill approach for fight-skill specifically, cross-referencing plugin.json version strings per commit (cae3360, e7084a6, cea50f9, f647168, 84c07fd, 7e2d954, d325469, ac228ca) against commit dates via git show.

<!-- handoff:learnings:end -->
