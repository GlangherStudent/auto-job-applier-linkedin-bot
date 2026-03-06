## Security Policy

This document explains how to report security issues and how security is handled in the Auto Job Applier project.

> **LinkedIn disclaimer**: For the legal disclaimer regarding LinkedIn automation, Terms of Service, and user responsibility, see the [Disclaimer (LinkedIn & Legal)](README.md#disclaimer-linkedin--legal) section in the README.

---

## Supported versions

This is an open-source project maintained on a best-effort basis.  
In general:

- the latest version on the default branch receives fixes and improvements,
- older versions are not actively supported.

---

## Reporting a vulnerability

If you believe you have found a security vulnerability, please **do not** open a public GitHub issue with sensitive details.

Instead:

1. Contact the maintainer privately using the email address listed in the repository profile or project metadata.
2. Include:
   - a clear description of the issue,
   - steps to reproduce,
   - the potential impact,
   - any suggested fixes or mitigations.

You can also open a minimal GitHub issue stating that a security vulnerability was found and that details were shared privately.

---

## Scope and assumptions

The Auto Job Applier project is designed with the following assumptions:

- It runs **locally** on a trusted machine that you control.
- It uses your own LinkedIn account and API keys.
- It is **not** intended to be run as a multi-tenant or publicly exposed service.

You are responsible for:

- protecting your LinkedIn credentials and API keys,
- controlling access to the machine where the bot and UI run,
- complying with LinkedIn’s Terms of Service and applicable laws in your jurisdiction.

---

## Handling of secrets and personal data

The project follows these principles:

- Secrets (LinkedIn credentials, API keys) are loaded from environment variables (`.env` file) using `python-dotenv`.
- The `.env` file is:
  - local to your machine,
  - **never** committed to version control (covered by `.gitignore`),
  - documented via `.env.example`.
- Configuration files in `config/` use **placeholders** in the repository:
  - you should replace these with your real data locally,
  - you should not commit your personal information.
- Runtime data:
  - CSV histories under `all excels/`,
  - logs under `logs/`,
  - local resumes under `all resumes/`,
  are considered **local artefacts** and are excluded from version control.

If you contribute code, do **not**:

- hard-code API keys, passwords, or tokens,
- log sensitive fields in plaintext unless absolutely necessary and clearly documented,
- commit real log files, CSV histories, or resumes.

---

## Web UI and network exposure

The Flask UI:

- is intended to run on `localhost` for personal use,
- has debug mode controlled by the `APP_DEBUG` environment variable (default: disabled),
- should not be exposed directly to the public internet without additional hardening and review.

If you choose to expose the UI beyond localhost, you are responsible for:

- configuring proper TLS termination and authentication,
- restricting access to trusted users,
- reviewing and adapting the code for your threat model.

---

## Responsible disclosure

We ask that you:

- act in good faith and avoid unnecessary harm,
- give the maintainers reasonable time to investigate and fix issues before public disclosure,
- avoid accessing data you do not own or are not authorised to view.

Thank you for helping keep this project and its users safe.

