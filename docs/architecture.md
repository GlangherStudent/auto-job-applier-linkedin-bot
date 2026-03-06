## Architecture

This document describes the current structure. For a concise overview, see the [README](../README.md) and the [Project Structure](../README.md#project-structure) section.

### High-level components

- **CLI bot (`runAiBot.py`)**
  - Main orchestrator for the automation flow.
  - Loads configuration from the `config/` package.
  - Uses modules under `modules/` for browser automation, anti-detection, smart answers, LLM integration, CSV handling, and error recovery.

- **Flask UI (`app.py`)**
  - Exposes:
    - `GET /` – serves `templates/index.html`.
    - `GET /applied-jobs` – returns the list of applied jobs as JSON.
    - `PUT /applied-jobs/<job_id>` – updates the “Date Applied” column in the history CSV.

- **Runtime data**
  - Application histories in `all excels/` (created at runtime).
  - Logs and checkpoints in `logs/` (created at runtime).
  - Local resumes in `all resumes/` (folder only, no CVs shipped in the repository).

### Key Python packages and modules

- `config/settings.py` – global bot and runtime settings (file paths, behaviour switches, anti-detection).
- `config/search.py` – LinkedIn search terms, filters, and location preferences.
- `config/personals.py` – personal data placeholders (name, phone, location, EEO answers).
- `config/questions.py` – answers for form questions (salary, notice period, LinkedIn headline/summary, etc.).
- `config/constants.py` – shared constants (conversion helpers, network limits, retry parameters, LinkedIn URLs).
- `config/keywords_db.json` – text templates and categories for `JobMatcher`.

Core modules under `modules/`:

- `open_chrome.py` – starts a Chrome/undetected-chromedriver instance.
- `clickers_and_finders.py` – robust element finding and clicking.
- `helpers.py` – logging, timing helpers, CSV-safe truncation, and date parsing.
- `validator.py` – strict validation of configuration values and paths.
- `application_state.py` – in-memory state about current session and counters.
- `csv_manager.py` – `CachedCSVManager`, a simple CSV cache with locking semantics.
- `anti_detection.py` – `HumanBehaviorSimulator` for human-like mouse movement, typing, scrolling, and micro-pauses.
- `session_manager.py` – break scheduling, daily limits, and checkpointing.
- `error_recovery.py` – retry decorators and structured error recovery for Selenium actions.
- `file_manager.py` – log and screenshot directory management and rotation.
- `job_matcher.py` – `JobMatcher` for matching free-text questions to categories/answers using TF-IDF and fuzzy matching.
- `smart_answers.py` – pattern-based select/radio/checkbox answers, including Yes/No strategies.
- `cv_selector.py` – selects the most appropriate resume file name (no uploads) based on the job description.
- `llm_field_helper.py` – builds prompts and calls LLMs when other strategies fail.
- `fallback_llm.py` – multi-provider LLM client with sequential fallback (Groq, Gemini, Mistral, gateways).

### Runtime flow (bot)

1. **Startup & validation**
   - User runs `python runAiBot.py` (or a helper script).
   - `config` modules are imported and validated by `modules.validator`.

2. **Browser & login**
   - `open_chrome` opens Chrome using either a standard or undetected profile, based on settings.
   - The bot attempts LinkedIn login using:
     - environment variables (`LINKEDIN_USERNAME`, `LINKEDIN_PASSWORD`), or
     - an existing logged-in browser profile, or
     - manual login if neither is available.

3. **Job search**
   - For each term in `config/search.search_terms`:
     - Sets `search_location`.
     - Applies LinkedIn filters (experience, job type, on-site/remote, etc.).
     - Iterates over paginated search results.

4. **Job filtering**
   - For each job card:
     - Extracts title, company, location, and tags.
     - Applies internal filters:
       - company/description “bad words” and whitelisted “good words”,
       - required experience vs. configured experience,
       - work location constraints when enabled.

5. **Easy Apply flow**
   - Opens the Easy Apply modal for eligible jobs.
   - Selects a resume by matching the desired DOCX file name (no new uploads).
   - Answers form fields in order:
     - direct mapping from `config/personals.py` or `config/questions.py`,
     - `SmartAnswers` for Yes/No and select-type questions,
     - `JobMatcher` for text responses,
     - `LLMFieldHelper` + `FallbackLLM` as a last resort for unknown text.

6. **Submission & outcome**
   - Clicks through `Next`/`Review`/`Submit` buttons where present.
   - On success:
     - writes a row to `all_applied_applications_history.csv`,
     - updates in-memory state and logs.
   - On failure:
     - writes a row to `all_failed_applications_history.csv` with error context,
     - may capture screenshots via `FileManager`.

7. **Sessions, breaks, and limits**
   - `SessionManager`:
     - tracks applications per session and per day,
     - schedules natural breaks with human-like timing,
     - stops or slows down as daily limits are approached.
   - Checkpoints are written to `logs/checkpoint.json` and reloaded on restart.

### Runtime flow (Flask UI)

1. User runs:

```bash
python app.py
```

2. Flask resolves the history CSV path from `config.settings.file_name` or falls back to
   `all excels/all_applied_applications_history.csv`.

3. Endpoints:
   - `GET /` – renders `templates/index.html`.
   - `GET /applied-jobs` – uses `CachedCSVManager.safe_read_dict_rows()` to read CSV rows and return them as JSON.
   - `PUT /applied-jobs/<job_id>` – updates `Date Applied` for the given job and invalidates the CSV cache.

### CI workflow

GitHub Actions runs on push and pull requests (see `.github/workflows/ci.yml`):

- Installs dependencies from `requirements.txt`
- Runs `python -m compileall .` as a basic syntax check

