## Contributing

Thank you for your interest in contributing to the Auto Job Applier project.  
This document explains how to propose changes and collaborate effectively.

---

## Code of conduct

- Be respectful and constructive.
- Assume good intent.
- Focus on technical issues, not individuals.

---

## Development workflow

### 1. Fork and clone

1. Fork the repository on GitHub to your own account.
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/auto-job-applier-linkedin-bot.git
cd auto-job-applier-linkedin-bot
```

3. Add the original repository as an `upstream` remote (optional but recommended):

```bash
git remote add upstream https://github.com/GlangherStudent/auto-job-applier-linkedin-bot.git
```

---

### 2. Branch naming

Create a feature branch from the default branch (usually `main` or `master`):

```bash
git checkout -b feature/short-description
```

Use one of the following prefixes:

- `feature/` – new features or enhancements,
- `fix/` – bug fixes,
- `docs/` – documentation only changes,
- `chore/` – tooling, CI, or housekeeping.

Examples:

- `feature/improve-anti-detection`
- `fix/csv-manager-deadlock`
- `docs/add-usage-examples`

---

### 3. Making changes

- Keep changes focused and scoped:
  - one logical change per pull request whenever possible.
- Follow existing code style and patterns:
  - keep comments concise and in English,
  - avoid committing real secrets, personal data, or real logs,
  - prefer configuration via `config/` and environment variables.
- Update or add documentation in `docs/` when you change behaviour or APIs.

If you introduce a new configuration option:

- document it in `docs/setup.md` and/or `docs/usage.md`,
- consider adding safe defaults and environment variable support where appropriate.

---

### 4. Tests and linting

Currently the project does not ship with a comprehensive automated test suite.  
However:

- do not introduce syntax errors or obvious breakages,
- run a basic check before opening a PR:

```bash
python -m compileall .
```

If you add tests, please:

- place them under a `tests/` folder,
- ensure they can run via a simple command (for example `pytest` or `python -m unittest`),
- update CI configuration (`.github/workflows/ci.yml`) to execute them.

---

### 5. Commit messages

Write clear, descriptive commit messages:

- Use the imperative mood: `Add session manager tests`, `Fix CSV path handling`.
- Keep the first line short (≤ 72 characters) and use additional lines for details.

Examples:

- `fix: handle missing CSV files in Flask UI`
- `feat: add configurable LLM timeout`

---

### 6. Pull request process

1. Make sure your branch is up to date with the default branch:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/short-description
git rebase main
```

2. Push your branch to your fork:

```bash
git push origin feature/short-description
```

3. Open a pull request:

- Target: the default branch of the original repository.
- Provide:
  - a clear title (what the PR does),
  - a short description:
    - motivation and context,
    - important implementation details,
    - breaking changes (if any),
    - configuration or documentation updates.

4. Be prepared to:

- respond to review comments,
- adjust your implementation,
- add or update documentation.

---

### 7. Security-sensitive changes

If your contribution touches security-sensitive areas:

- environment variable handling,
- authentication or credential storage,
- logging of potentially sensitive data,

please highlight this in the PR description and reference the `SECURITY.md` guidelines.

---

### 8. License

By contributing, you agree that your contributions will be licensed under the same license as this project (GNU Affero General Public License v3 or later).

