"""
CV Selector - choose the most appropriate resume file from a folder based on the job description.
Uses FallbackLLM for semantic analysis when multiple resumes are available.
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from modules.fallback_llm import get_fallback_llm
except ImportError:
    get_fallback_llm = None

# Maximum characters for CV summary and truncated job description
CV_SNIPPET_CHARS = 500
JD_TRUNCATE_CHARS = 1500


def _extract_text_from_pdf(pdf_path: str, max_chars: int = CV_SNIPPET_CHARS) -> str:
    """Extract text from the first pages of a PDF (best-effort).

    Note: For DOC/DOCX files we do not parse the content here – selection is primarily
    based on the file name, which should match the name already stored in LinkedIn.
    """
    if PdfReader is None:
        return "(PyPDF2 not available)"
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        total = 0
        for i, page in enumerate(reader.pages):
            if i >= 2:  # Max 2 pagini
                break
            t = page.extract_text() or ""
            text_parts.append(t)
            total += len(t)
            if total >= max_chars:
                break
        result = " ".join(text_parts).replace("\n", " ").strip()
        return result[:max_chars] if len(result) > max_chars else result
    except Exception:
        return "(error reading PDF)"


def _get_cv_files(cv_folder: str) -> List[Tuple[str, str]]:
    """
    Return the list of (absolute_path, file_name) tuples for all resumes in the folder.

    Important for the LinkedIn flow:
    - locally, in `all resumes/cv`, resumes are expected in DOCX format,
    - in LinkedIn’s application section, files must have EXACTLY the same names,
    - the bot does NOT upload new files, it only selects the correct resume by name.
    """
    base = Path(cv_folder)
    if not base.is_absolute():
        base = Path(__file__).resolve().parent.parent / cv_folder
    if not base.exists() or not base.is_dir():
        return []

    files: List[Tuple[str, str]] = []

    # Prefer DOCX resumes (format used locally and in LinkedIn)
    for pattern in ("*.docx", "*.doc", "*.pdf"):
        for f in sorted(base.glob(pattern)):
            files.append((str(f.resolve()), f.name))

    return files


def select_best_resume(
    job_description: str,
    cv_folder: str = "all resumes/cv",
) -> Optional[str]:
    """
    Choose the best matching resume for the job based on the job description.

    Args:
        job_description: Job description text.
        cv_folder: Folder containing resumes (path relative to the project root).

    Returns:
        Absolute path of the recommended resume file, or None if no resumes are available
        or the LLM-based selection fails.
    """
    cv_files = _get_cv_files(cv_folder)
    if not cv_files:
        return None

    if len(cv_files) == 1:
        path, name = cv_files[0]
        print(f"[CV-Selector] Single CV detected, using: {name}")
        return path

    if get_fallback_llm is None:
        path, name = cv_files[0]
        print(f"[CV-Selector] Fallback (no LLM) – using first CV: {name}")
        return path

    # Build short summaries for each resume
    cv_summaries = []
    for path, name in cv_files:
        snippet = ""
        # For PDFs try to extract a portion of the content;
        # for DOC/DOCX we keep the summary based on the file name only.
        if Path(path).suffix.lower() == ".pdf":
            snippet = _extract_text_from_pdf(path)
        cv_summaries.append(f"- {name}: {snippet[:300]}..." if snippet else f"- {name}")

    jd_short = (job_description or "Unknown job")[:JD_TRUNCATE_CHARS]
    cv_list = "\n".join(cv_summaries)
    file_names = ", ".join(name for _, name in cv_files)

    prompt = f"""Job Description:
{jd_short}

Available resumes (first lines of each):
{cv_list}

Which resume file is the best match for this job? Reply with ONLY the exact filename (e.g. CV1.pdf), nothing else."""

    system = "You are a recruiter. Pick the resume that best matches the job. Reply ONLY with the filename."

    try:
        llm = get_fallback_llm()
        response, provider_name = llm.generate(prompt, system_prompt=system)
        response = response.strip()
        # Clean up quotation marks and surrounding whitespace
        response = response.strip('"\'')
        # Find the matching path
        for path, name in cv_files:
            if name.lower() == response.lower():
                print(f"[CV-Selector] LLM ({provider_name}) chose resume: {name}")
                return path
        # Fallback: primul CV
    except Exception as e:
        print(f"[CV-Selector] LLM-based selection failed: {type(e).__name__} - {str(e)[:120]}")

    # Fallback: first resume, with log
    path, name = cv_files[0]
    print(f"[CV-Selector] Fallback (LLM error) – using first CV: {name}")
    return path


def get_resume_path_for_job(
    job_description: str,
    cv_folder: str = "all resumes/cv",
    default_resume_path: str = "all resumes/default/resume.docx",
) -> str:
    """
    Return the resume path to use for this job.
    If there are resumes in cv_folder, choose the best; otherwise use the default path.
    """
    selected = select_best_resume(job_description, cv_folder)
    if selected:
        return selected
    base = Path(__file__).resolve().parent.parent
    default_full = base / default_resume_path
    if default_full.exists():
        return str(default_full)
    return default_resume_path
