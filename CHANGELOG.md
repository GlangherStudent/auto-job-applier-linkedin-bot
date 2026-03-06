# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Initial public open-source hardening:
  - environment variable template for LinkedIn and LLM providers (`.env.example`),
  - documentation suite under `docs/` (overview, architecture, setup, usage),
  - security policy (`SECURITY.md`),
  - contribution guidelines (`CONTRIBUTING.md`),
  - basic project structure and ignore rules for runtime data and virtual environments.
- Clarified configuration files with safe placeholders for personal data in `config/personals.py` and `config/questions.py`.
- Safer defaults for the Flask UI:
  - debug mode controlled via `APP_DEBUG`,
  - configurable port via `APP_PORT`.

### Changed
- Normalised comments and messages to clear, professional English across core modules and configuration files.
- Cleaned `.gitignore` to exclude environment files, virtual environments, logs, CSV histories, and other runtime artefacts.

### Removed
- Committed `.env` file that previously contained real credentials and API keys.
- Committed runtime logs and application history CSVs containing personal and job-related data.

## [0.1.0] – Initial internal version (pre-open-source)

- Original implementation of the LinkedIn Easy Apply automation bot.
- Early versions of:
  - configuration modules under `config/`,
  - Selenium/undetected-chromedriver automation under `modules/`,
  - basic session management, CSV logging, and error recovery,
  - minimal Flask UI for viewing applied jobs history.

