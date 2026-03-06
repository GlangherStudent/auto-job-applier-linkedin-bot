## Auto Job Applier for LinkedIn

Automation bot that applies to **LinkedIn Easy Apply** jobs using your configured search criteria, personal data, and smart form answers â€“ plus a lightweight web UI to review and update your application history.

---

## Badges

[![License](https://img.shields.io/badge/license-AGPLv3-blue.svg)](LICENSE) [![Stars](https://img.shields.io/github/stars/GlangherStudent/auto-job-applier-linkedin-bot?style=social)](https://github.com/GlangherStudent/auto-job-applier-linkedin-bot) [![Issues](https://img.shields.io/github/issues/GlangherStudent/auto-job-applier-linkedin-bot)](https://github.com/GlangherStudent/auto-job-applier-linkedin-bot/issues) [![Last Commit](https://img.shields.io/github/last-commit/GlangherStudent/auto-job-applier-linkedin-bot)](https://github.com/GlangherStudent/auto-job-applier-linkedin-bot/commits/main)

---

## Overview

Auto Job Applier is a **local automation tool** that:

- opens Chrome and logs into LinkedIn,
- searches for jobs based on configurable titles, locations, and filters,
- automatically completes Easy Apply forms using your configuration,
- leverages multiple LLM providers to generate smart free-text answers,
- stores a full history of applied and failed applications in CSV files,
- exposes a small Flask-based UI to browse and manage applied jobs.

The project is intended for **personal use only** on your own machine and account.

---

## Features

- **Configurable job search**
  - multiple `search_terms` and `search_location`,
  - LinkedIn filters (experience level, job type, on-site/remote),
  - internal keyword filters to skip irrelevant companies and roles.

- **Smart Easy Apply automation**
  - fills personal details from `config/personals.py`,
  - reuses predefined answers from `config/questions.py`,
  - uses `JobMatcher` (TF-IDF + fuzzy matching) for text answers,
  - uses multiple LLM providers as a fallback for unknown questions.

- **Resume selection without uploads**
  - selects among your already uploaded LinkedIn resumes by matching file names,
  - no new file uploads performed by the bot.

- **Anti-detection behaviour**
  - human-like mouse movement, typing, scrolling, and reading delays,
  - configurable daily limits and session breaks.

- **History and UI**
  - detailed CSV history of applied and failed jobs,
  - Flask UI to inspect applications and mark external links as applied.

---

## Tech Stack

- **Languages**: Python, HTML, JavaScript.
- **Automation**: `selenium`, `undetected-chromedriver`, `pyautogui`.
- **Web**: `Flask`.
- **LLM / AI**: `openai`, `google-generativeai`, `mistralai`, HTTP gateways.
- **NLP / scoring**: `scikit-learn`, `fuzzywuzzy`, `python-Levenshtein`.
- **Configuration & env**: `python-dotenv`.

See `requirements.txt` for the full list of dependencies.

---

## Architecture

At a high level:

- `runAiBot.py` is the main entrypoint for the automation bot.
- `config/` contains configuration for:
  - personal data and answers,
  - LinkedIn search preferences and anti-detection settings,
  - shared constants and keyword templates.
- `modules/` contains the implementation of:
  - browser automation and helpers,
  - session management and anti-detection,
  - CSV and file management,
  - JobMatcher, SmartAnswers, CV selector, LLM integration.
- `app.py` exposes a small Flask UI and JSON API for applied jobs.
- `templates/index.html` is the frontend for the applied jobs history.

For a deeper breakdown, see:

- `docs/architecture.md`
- `docs/overview.md`

---

## Project Structure

High-level structure:

- `runAiBot.py` â€“ CLI entrypoint for the LinkedIn bot.
- `app.py` â€“ Flask app for the applied jobs UI.
- `config/` â€“ all configuration modules (personal data, questions, search, settings, constants).
- `modules/` â€“ core logic modules (automation, matching, anti-detection, CSV, LLM, etc.).
- `templates/` â€“ HTML template(s) for the Flask UI.
- `docs/` â€“ documentation (overview, architecture, setup, usage).
- `scripts/` â€“ auxiliary scripts (for example, LLM provider tests).
- `all excels/` â€“ runtime CSV history (ignored by Git).
- `all resumes/` â€“ local resumes folder (ignored by Git).
- `logs/` â€“ runtime logs and checkpoints (ignored by Git).

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/auto-job-applier-linkedin.git
cd auto-job-applier-linkedin
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # macOS / Linux
```

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

Edit `.env` and fill in:

- `LINKEDIN_USERNAME`, `LINKEDIN_PASSWORD`,
- one or more LLM provider keys (`GROQ_API_KEY`, `GEMINI_API_KEY`, etc.),
- optionally `APP_DEBUG` and `APP_PORT` for the Flask UI.

5. **Configure personal data and answers**

Update:

- `config/personals.py` â€“ name, phone, city, address, EEO answers (placeholders in the repo).
- `config/questions.py` â€“ salary ranges, notice period, LinkedIn headline, summary, cover letter, and dropdown strategies.
- `config/search.py` â€“ job titles, locations, and LinkedIn filters.
- `config/settings.py` â€“ global runtime and anti-detection settings.

For detailed configuration guidance, read:

- `docs/setup.md`
- `docs/usage.md`

---

## Environment Variables

The project uses environment variables for all secrets and sensitive configuration.  
They are documented in `.env.example` and include:

- `LINKEDIN_USERNAME`, `LINKEDIN_PASSWORD`,
- `GROQ_API_KEY`, `GEMINI_API_KEY`, `MISTRAL_API_KEY`,
- `OPENROUTER_API_KEY`, `HF_API_KEY`,
- `LLMGATEWAY_API_KEY_1`, `LLMGATEWAY_API_KEY_2`, `LLMGATEWAY_API_KEY_3`,
- `APP_DEBUG`, `APP_PORT`.

**Never** commit your `.env` file. It is ignored by `.gitignore`.

---

## Usage

### Run the bot

```bash
python runAiBot.py
```

The bot will:

- validate configuration,
- open Chrome and log into LinkedIn,
- search according to your configured terms and filters,
- apply to Easy Apply jobs and record results in CSV files.

### Run the web UI

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

You will see a table of applied jobs with:

- job title and company,
- HR contact and links,
- external application links,
- a check mark when a job is marked as applied.

Clicking an external link also updates the `Date Applied` column in the CSV.

For a complete usage guide, see `docs/usage.md`.

---

## Example Workflow

1. Configure search and personal data under `config/`.
2. Start the bot with `python runAiBot.py`.
3. Let it run until the daily limit or your own stopping criteria.
4. Review results:
   - directly via CSV files under `all excels/`,
   - or via the Flask UI at `http://localhost:5000`.
5. Adjust filters, answers, and LLM behaviour based on results.

---

## Documentation

Additional documentation is available in the `docs/` folder:

- `docs/overview.md`
- `docs/architecture.md`
- `docs/setup.md`
- `docs/usage.md`
- `docs/GITHUB_PUBLICATION.md` – GitHub topics, description, and publication checklist

---

## Development

Basic development steps:

```bash
git clone https://github.com/YOUR_USERNAME/auto-job-applier-linkedin.git
cd auto-job-applier-linkedin
python -m venv venv
venv\Scripts\activate        # or source venv/bin/activate
pip install -r requirements.txt
python -m compileall .       # quick syntax check
```

CI is configured via GitHub Actions in `.github/workflows/ci.yml`:

- installs dependencies from `requirements.txt`,
- runs `python -m compileall .` as a basic safety check.

See `CONTRIBUTING.md` for details on branching, commits, and pull requests.

---

## Contributing

Contributions are welcome.  
Please read:

- `CONTRIBUTING.md` â€“ development workflow and expectations,
- `CHANGELOG.md` â€“ notable changes and release notes.

---

## Security

Auto Job Applier is intended for **local, personal use only**.  
Before using it:

- carefully review `SECURITY.md`,
- keep your `.env` file private,
- do not expose the Flask UI directly to the public internet without additional hardening.

If you find a security issue, please follow the responsible disclosure process described in `SECURITY.md`.

---

## Changelog

Changes are tracked in:

- `CHANGELOG.md`

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**.  
See:

- `LICENSE`
- <https://www.gnu.org/licenses/agpl-3.0.en.html>

---

## Disclaimer (LinkedIn & Legal)

> **This project is provided for educational and research purposes only.**
>
> Using automation on LinkedIn may violate LinkedIn's Terms of Service and acceptable use policies. You are solely responsible for how you use this software and for complying with LinkedIn's Terms of Service and all applicable laws and regulations.
>
> The authors and contributors are not affiliated with LinkedIn and do not assume any responsibility for account limitations, bans, or other consequences arising from the use of this tool.

---
