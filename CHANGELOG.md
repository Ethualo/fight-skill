# Changelog

이 프로젝트의 버전별 변경 이력이다. [Keep a Changelog](https://keepachangelog.com/) 형식을 따른다.
`0.1.0` 이전 상세 커밋 이력은 `git log`를 참고한다.

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
