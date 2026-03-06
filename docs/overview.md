## Overview

The Auto Job Applier project automates LinkedIn **Easy Apply** job applications and provides a small web UI to inspect application history.

> For a quick start, see the main [README](../README.md). The project structure (`runAiBot.py`, `app.py`, `config/`, `modules/`, `docs/`, `scripts/`) is described there.

- **Automation bot**: runs in a local browser (Chrome) and:
  - logs into LinkedIn using your account (or an already logged-in profile),
  - searches for jobs based on configurable titles, locations, and filters,
  - filters out irrelevant roles,
  - completes Easy Apply forms using your personal data and predefined answers,
  - optionally uses LLM providers to generate smart free-text answers,
  - keeps a CSV history of all successful and failed applications.
- **Web UI**: a minimal Flask app that:
  - reads the CSV of applied jobs,
  - exposes it as JSON,
  - renders a simple HTML table to browse and mark jobs as “applied” for external links.

The project is designed for **local, personal use only** on a trusted machine. It is not meant to be hosted as a public service or shared with third parties.

