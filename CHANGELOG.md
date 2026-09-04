# Changelog

이 프로젝트의 버전별 변경 이력이다. [Keep a Changelog](https://keepachangelog.com/) 형식을 따른다.
`0.1.0` 이전 상세 커밋 이력은 `git log`를 참고한다.

## [0.3.11] - 2026-09-04

### Added

- `fight-clarify`에 해석자 컨텍스트 상한 절 추가 (`fight-audit` 제안자 상한과 동일 적용, `AGENTS.md`에도 명시)
- `fight-audit` 감사자 지적에 `[대상: 지시|제안안]` 태그 추가 — 태그 누락은 `[대상: 지시]`로 간주, 기존 `해결`/`기각` 증거 요건은 그대로 유지

## [0.3.10] - 2026-09-04

### Fixed

- `fight-clarify`에서 근거 없는 공통 가정을 확정하지 않고 미확정 항목으로 유지
- `fight-audit`에서 모든 `BLOCK`의 처리 결과를 보존하고 `미검증` 판정과 확정 보류 규칙 추가
- clarify 진행 중 사용자 질문에서 같은 스킬로 재진입하는 옵션 제외
- 한국어 README 모델 정책과 세 배포 버전 갱신 안내 동기화

### Added

- 세 매니페스트·두 README·변경 이력의 일치를 확인하는 `scripts/check_release.py`

## [0.3.9] - 2026-09-04

### Changed

- `fight-clarify`의 Claude Code 두 호출 모델을 부모 세션 상속에서 `sonnet` 고정으로 변경 (`skills/fight-clarify/SKILL.md`, `CLAUDE.md`, `AGENTS.md`, `README.md`)

## [0.3.8] - 2026-09-02

### Changed

- `fight-clarify`의 두 서브에이전트가 서로 검증하지 않는다는 사실을 `CLAUDE.md`·`AGENTS.md`에 명시
- `skills/fight-clarify/SKILL.md`의 질문 조건 문구를 명확화 (일치 부분은 재확인 안 하고 갈린 부분만 질문으로 올림)

## [0.3.7] - 2026-08-31

### Changed

- 플러그인 동작·설치 안내 문서 명확화

## [0.3.6] - 2026-08-31

### Fixed

- Codex reasoning effort 표기를 `low`/`medium`/`high`/`xhigh`/`max`/`ultra` 6단계로 정정

### Docs

- Codex `fight-audit` 라이브 검증 결과 반영, 문서 중복 정리
- 공개 배포용 README·CONTRIBUTING·LICENSE 추가

## [0.3.5] - 2026-08-31

### Changed

- 듀얼 플랫폼(Claude Code·Codex) 플러그인 계약 정렬

## [0.3.1] - 2026-08-31

### Added

- Claude Code·Codex 듀얼 플랫폼 지원

## [0.2.0] - 2026-08-27

### Added

- `fight-audit` 서브에이전트 모델(제안자·감사자) 명시 고정

## [0.1.0] - 2026-08-27

### Added

- `fight-audit` 스킬과 플러그인 매니페스트 최초 추가
