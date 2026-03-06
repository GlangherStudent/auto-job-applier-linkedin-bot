"""
Test tool for all LLM providers configured in `modules.fallback_llm`.

How to run:
    1) Activate your virtual environment (for example using start.bat or manually).
    2) From the project root, run:
           python scripts/test_llm_providers.py

The script will sequentially test:
    Groq -> Gemini -> Mistral -> OpenRouter -> HuggingFace -> LLM API (x3)
and print whether each provider responds correctly.
"""

import os
import sys


# Add the project root to sys.path so we can import `modules`
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.fallback_llm import FallbackLLM


def main() -> None:
    llm = FallbackLLM()
    prompt = "Reply with the single word 'OK' if you are working correctly."
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]

    print("\n=== LLM providers test ===\n")

    for name, get_provider in llm.providers:
        print(f"\n--- Test {name} ---")
        try:
            provider = get_provider()
            # Use the internal method to force each provider individually
            content = llm._call_provider(provider, messages, prompt)  # type: ignore[attr-defined]
            short = (content or "").strip().replace("\n", " ")
            if len(short) > 120:
                short = short[:117] + "..."
            print(f"STATUS: OK ({provider['name']})")
            print(f"Response: {short or '[empty]'}")
        except Exception as e:
            print(f"STATUS: FAILED ({name})")
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

