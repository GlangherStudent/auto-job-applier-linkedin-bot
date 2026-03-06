## Setup

This guide aligns with the main [README](../README.md). For publishing the project on GitHub, see [GITHUB_PUBLICATION.md](GITHUB_PUBLICATION.md).

### 1. Prerequisites

- **Operating system**: Windows, macOS, or Linux.
- **Python**: version 3.10 or newer.
- **Google Chrome**: installed in the default location for your OS.

> The bot uses `undetected-chromedriver` by default and does not require a separate ChromeDriver binary when stealth mode is enabled.

### 2. Clone the repository

```bash
git clone https://github.com/GlangherStudent/auto-job-applier-linkedin-bot.git
cd auto-job-applier-linkedin-bot
```

If you downloaded a ZIP archive instead, extract it and open the folder in your terminal.

### 3. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # macOS / Linux
```

### 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:

- browser automation: `selenium`, `undetected-chromedriver`, `pyautogui`,
- web: `flask`, `flask-cors`,
- data: `PyPDF2`, `scikit-learn`, `fuzzywuzzy`, `python-Levenshtein`,
- configuration: `python-dotenv`,
- LLM clients: `openai`, `google-generativeai`, `mistralai`, `requests`.

### 5. Configure environment variables

1. Copy the example file:

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows (PowerShell or CMD)
```

2. Edit `.env` and fill in:

- LinkedIn:
  - `LINKEDIN_USERNAME`
  - `LINKEDIN_PASSWORD`
- LLM providers (only the ones you use):
  - `GROQ_API_KEY`
  - `GEMINI_API_KEY`
  - `MISTRAL_API_KEY`
  - `OPENROUTER_API_KEY`
  - `HF_API_KEY`
  - `LLMGATEWAY_API_KEY_1`
  - `LLMGATEWAY_API_KEY_2`
  - `LLMGATEWAY_API_KEY_3`
- Optional Flask settings:
  - `APP_DEBUG` (`true` / `false`, default `false`)
  - `APP_PORT` (default `5000`)

> Never commit your `.env` file – it is already ignored by `.gitignore`.

### 6. Configure personal data and answers

Edit the configuration files under `config/`:

- `config/personals.py`
  - Replace placeholders such as:
    - `YOUR_FIRST_NAME`, `YOUR_LAST_NAME`,
    - `+10000000000`,
    - `Your City, Your Country`,
    - `Your Street and Number`, `Your State or Region`, `Your Country`.
  - Optionally set EEO-related fields if you want the bot to answer them.

- `config/questions.py`
  - Adjust:
    - `default_resume_path`, `resume_cv_folder`,
    - `years_of_experience`,
    - `desired_salary`, `desired_salary_max`, `current_ctc`,
    - `notice_period`,
    - `linkedin_headline`, `linkedin_summary`, `cover_letter`,
    - `recent_employer`, `education`, `date_of_birth`, `languages_spoken`, `university_name`,
    - `dropdown_answer_strategy`, `my_skills_and_certifications`, `my_experience_years`,
    - `custom_dropdown_answers`.

- `config/search.py`
  - Configure:
    - `search_terms` (job titles),
    - `search_location`,
    - LinkedIn filters (experience level, job type, on-site/remote),
    - keyword-based filters for companies and job descriptions,
    - location filters when you want to restrict where you apply.

- `config/settings.py`
  - Review:
    - output paths (`file_name`, `failed_file_name`, `logs_folder_path`),
    - `click_gap`, `run_in_background`, `safe_mode`, `stealth_mode`,
    - anti-detection flags,
    - `daily_application_limit` and session/break parameters.

### 7. Create runtime folders

The code will create missing folders when needed, but you may want to ensure these exist:

- `all excels/`
- `all resumes/` (and optionally `all resumes/default/`, `all resumes/cv/`)
- `logs/`

These folders are ignored by Git so that your personal data and logs are never committed.

