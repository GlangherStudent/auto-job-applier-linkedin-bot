"""
LLM Field Helper - use FallbackLLM to answer unknown fields in Easy Apply forms.
"""

from typing import Optional, List, Dict, Any

try:
    from modules.fallback_llm import get_fallback_llm
except ImportError:
    get_fallback_llm = None


def _load_context() -> Dict[str, Any]:
    """Load PERSONALS + QUESTIONS_PERSONAL for LLM context."""
    try:
        from config.personals import PERSONALS
        from config.questions import QUESTIONS_PERSONAL
        ctx = dict(PERSONALS)
        ctx.update(QUESTIONS_PERSONAL)
        return ctx
    except ImportError:
        return {}


def ask_llm_for_field(
    question_label: str,
    field_type: str,
    options: Optional[List[str]] = None,
    job_description: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Ask the LLM for an answer to an unknown field.

    Args:
        question_label: Question text (field label).
        field_type: "select" | "radio" | "text".
        options: List of options for select/radio (visible text only).
        job_description: Shortened job description (optional).
        context: Override for candidate data (optional).

    Returns:
        The LLM answer or None if it fails.
    """
    if get_fallback_llm is None:
        return None

    ctx = context or _load_context()
    ctx_str = "\n".join(f"  {k}: {v}" for k, v in ctx.items() if v)

    jd_short = (job_description or "")[:800].replace("\n", " ")

    options_part = ""
    if options:
        options_part = f"\nOptions (respond with EXACTLY one from this list):\n" + "\n".join(f"  - {o}" for o in options)

    system = """You are filling a job application form. Use ONLY the candidate data below.
For selects/radios, respond with EXACTLY one option from the list.
Respond with ONLY the answer - one option or short text. No explanation, no preamble."""

    prompt = f"""Candidate data:
{ctx_str}

Job context:
{jd_short}

Question: "{question_label}"
Field type: {field_type}{options_part}

Your answer (only the value):"""

    try:
        llm = get_fallback_llm()
        response, _ = llm.generate(prompt, system_prompt=system)
        response = (response or "").strip()
        if not response:
            return None
        # Clean quotes and newlines
        response = response.strip('"\'"\n\t')
        # For select/radio, ensure the answer is one of the available options
        if options and response:
            opt_lower = [o.strip().lower() for o in options]
            resp_lower = response.lower()
            for i, o in enumerate(options):
                if o.strip().lower() == resp_lower or resp_lower in o.strip().lower():
                    return o.strip()
            # Partial match
            for o in options:
                if resp_lower in o.lower():
                    return o.strip()
        return response
    except Exception:
        return None
