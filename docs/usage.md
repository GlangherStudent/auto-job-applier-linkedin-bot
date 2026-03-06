## Usage

This document explains how to run the LinkedIn Auto Job Applier bot and the optional web UI. For installation and configuration, see [setup.md](setup.md) and the main [README](../README.md).

---

### 1. Running the bot (CLI)

After completing the setup and configuration steps, start the bot from the project root:

```bash
python runAiBot.py
```

The high-level flow is:

1. Validate configuration (paths, types, required values).
2. Start Chrome via Selenium/undetected-chromedriver.
3. Log into LinkedIn using your credentials or an existing logged-in profile.
4. Iterate through your configured `search_terms` and `search_location`.
5. Apply LinkedIn filters (experience, job type, work location).
6. Filter job cards with internal rules (blacklists, location, experience).
7. Open Easy Apply and complete the form for each eligible job.
8. Save results to CSV and log files.

The bot stops when:

- There are no more jobs available for the configured searches, or
- The `daily_application_limit` is reached, or
- LinkedIn shows a daily submissions limit message.

---

### 2. Interpreting CSV outputs

The bot writes two main CSV files under `all excels/` (created at runtime):

- `all_applied_applications_history.csv`
  - Successful applications or saved jobs with a positive status.
  - Typical columns:
    - `Job_ID`, `Job_Title`, `Company`, `HR_Name`, `HR_Link`,
    - `Job_Link`, `External_Job_link`, `Date_Applied`, etc.

- `all_failed_applications_history.csv`
  - Attempts that did not successfully complete (for example, submit button not found).
  - Includes:
    - job metadata,
    - reason for failure,
    - optional screenshot references.

You can open these files with Excel, Google Sheets, or any CSV viewer to audit what the bot has done.

---

### 3. Using the web UI

Start the Flask application from the project root:

```bash
python app.py
```

By default the app runs on `http://localhost:5000` (or on the port configured via `APP_PORT`).

In your browser, open:

```text
http://localhost:5000
```

You will see a table with:

- serial number,
- job title (clickable link to the job on LinkedIn),
- company name,
- HR contact and link (when available),
- external application link (for non-Easy-Apply jobs),
- a check mark indicating whether the job is marked as applied.

When you click an **External Link**:

- The UI will send a `PUT /applied-jobs/<job_id>` request to the backend.
- The backend updates the `Date Applied` column in the CSV and marks the job as applied.

If the history CSV does not exist yet, `GET /applied-jobs` returns a 404 with a clear JSON error message.

---

### 4. Example end-to-end workflow

1. **Prepare configuration**
   - Set personal data and answers in `config/personals.py` and `config/questions.py`.
   - Configure searches and filters in `config/search.py`.
   - Tune behaviour (daily limits, anti-detection) in `config/settings.py`.

2. **Start the bot**
   - Run `python runAiBot.py`.
   - Allow it to log in and run unattended, monitoring logs if desired.

3. **Review results**
   - Inspect `all excels/all_applied_applications_history.csv` and `all excels/all_failed_applications_history.csv`.
   - Optionally start the web UI with `python app.py` and browse to `http://localhost:5000`.

4. **Iterate**
   - Adjust filters and search terms based on results.
   - Refine answers and LLM behaviour to increase the quality of applications.

---

### 5. Safety and responsibility

- This project is intended **only for personal use** on your own LinkedIn account.
- You are responsible for:
  - complying with LinkedIn’s Terms of Service and anti-bot policies,
  - complying with applicable laws and regulations in your jurisdiction,
  - protecting your LinkedIn credentials and API keys.
- The authors and contributors do not accept liability for:
  - blocked accounts,
  - legal or policy-related consequences,
  - direct or indirect losses resulting from use of this code.

