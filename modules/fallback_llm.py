"""
FallbackLLM - multi-provider LLM with sequential fallback.
Groq -> Gemini -> Mistral -> OpenRouter -> HuggingFace -> LLM API (x3).
Used for CV selection and for answering unknown form fields.
LLM API: https://docs.llmapi.ai/ - OpenAI-compatible, keys starting with llmgtwy_*.
"""

import os
import time
import requests
from typing import Dict, Any, Optional, Tuple

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def _get_api_key(name: str) -> str:
    """
    Read an API key from an environment variable.
    Raise a clear error if it is not set.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Lipsa cheie API pentru {name}. Configureaz-o in fisierul .env sau in variabilele de sistem."
        )
    return value

# Lazy imports for providers
_openai_client = None
_gemini_configured = False
_mistral_client = None


def _get_openai_client(base_url: str, api_key: str):
    """Lazy init for OpenAI-compatible clients (Groq, OpenRouter, gateways)."""
    global _openai_client
    try:
        from openai import OpenAI
        return OpenAI(base_url=base_url, api_key=api_key)
    except ImportError:
        raise ImportError("openai package required: pip install openai")


def _get_groq() -> Dict[str, Any]:
    return {
        "name": "Groq",
        "client": _get_openai_client("https://api.groq.com/openai/v1", _get_api_key("GROQ_API_KEY")),
        "model": "llama-3.3-70b-versatile",
        "type": "openai",
    }


def _get_gemini() -> Dict[str, Any]:
    global _gemini_configured
    try:
        import google.generativeai as genai
        if not _gemini_configured:
            genai.configure(api_key=_get_api_key("GEMINI_API_KEY"))
            _gemini_configured = True
        return {
            "name": "Gemini",
            "model": "gemini-2.5-flash",
            "type": "gemini",
            "genai": genai,
        }
    except ImportError:
        raise ImportError("google-generativeai required: pip install google-generativeai")


def _get_mistral() -> Dict[str, Any]:
    try:
        from mistralai import Mistral
        return {
            "name": "Mistral",
            "client": Mistral(api_key=_get_api_key("MISTRAL_API_KEY")),
            "model": "mistral-large-latest",
            "type": "mistral",
        }
    except ImportError:
        raise ImportError("mistralai required: pip install mistralai")


def _get_openrouter() -> Dict[str, Any]:
    return {
        "name": "OpenRouter",
        "client": _get_openai_client("https://openrouter.ai/api/v1", _get_api_key("OPENROUTER_API_KEY")),
        # Popular, currently supported model on OpenRouter
        "model": "google/gemma-2-9b-it:free",
        "type": "openai",
    }


def _get_huggingface() -> Dict[str, Any]:
    return {
        "name": "Hugging Face",
        "api_key": _get_api_key("HF_API_KEY"),
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "type": "hf",
    }


def _get_llmapi_1() -> Dict[str, Any]:
    """LLM API (docs.llmapi.ai) - OpenAI-compatible gateway."""
    return {
        "name": "LLM API 1",
        "client": _get_openai_client("https://api.llmapi.ai/v1", _get_api_key("LLMGATEWAY_API_KEY_1")),
        "model": "gpt-4o",
        "type": "openai",
    }


def _get_llmapi_2() -> Dict[str, Any]:
    """LLM API (docs.llmapi.ai) - OpenAI-compatible gateway."""
    return {
        "name": "LLM API 2",
        "client": _get_openai_client("https://api.llmapi.ai/v1", _get_api_key("LLMGATEWAY_API_KEY_2")),
        "model": "gpt-4o",
        "type": "openai",
    }


def _get_llmapi_3() -> Dict[str, Any]:
    """LLM API (docs.llmapi.ai) - OpenAI-compatible gateway."""
    return {
        "name": "LLM API 3",
        "client": _get_openai_client("https://api.llmapi.ai/v1", _get_api_key("LLMGATEWAY_API_KEY_3")),
        "model": "gpt-4o",
        "type": "openai",
    }


class FallbackLLM:
    def __init__(self):
        # Build the provider list dynamically, only for keys that are actually configured.
        configured_providers = []

        def _safe_add(name: str, factory):
            try:
                # Each factory reads its own key; if it is missing it raises RuntimeError.
                factory()
                configured_providers.append((name, factory))
            except Exception as e:
                # Do not block the entire fallback chain because one provider is not configured.
                try:
                    msg = str(e)[:80]
                except Exception:
                    msg = "unknown"
                print(f"Provider {name} disabled (missing key or error): {msg}")

        _safe_add("groq", _get_groq)
        _safe_add("gemini", _get_gemini)
        _safe_add("mistral", _get_mistral)
        # OpenRouter and Hugging Face remain optional; they can be re-enabled easily if needed.
        # _safe_add("openrouter", _get_openrouter)
        # _safe_add("huggingface", _get_huggingface)
        _safe_add("llmapi_1", _get_llmapi_1)
        _safe_add("llmapi_2", _get_llmapi_2)
        _safe_add("llmapi_3", _get_llmapi_3)

        if not configured_providers:
            raise RuntimeError("No LLM provider is configured. Please check your API keys in the environment.")

        self.providers = configured_providers

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant. Respond with only the requested answer, no explanation.",
    ) -> Tuple[str, str]:
        """
        Generate a response using the first available provider.
        Returns a tuple: (content, provider_name).
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        last_error = None
        for provider_name, get_provider in self.providers:
            try:
                provider = get_provider()
                content = self._call_provider(provider, messages, prompt)
                if content and content.strip():
                    return content.strip(), provider["name"]
            except Exception as e:
                last_error = e
                try:
                    err_msg = str(e)[:100]
                except Exception:
                    err_msg = "unknown"
                print(f"Attempt with provider {provider_name} failed: {err_msg}... continuing with next provider...")
                time.sleep(2)

        raise Exception(f"Toate providerii au esuat. Ultimul: {last_error}")

    def _call_provider(
        self,
        provider: Dict[str, Any],
        messages: list,
        prompt: str,
    ) -> str:
        ptype = provider["type"]

        if ptype == "openai":
            response = provider["client"].chat.completions.create(
                model=provider["model"],
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            return response.choices[0].message.content or ""

        elif ptype == "gemini":
            model = provider["genai"].GenerativeModel(provider["model"])
            response = model.generate_content(prompt)
            return response.text or ""

        elif ptype == "mistral":
            chat_response = provider["client"].chat.complete(
                model=provider["model"],
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            return chat_response.choices[0].message.content or ""

        elif ptype == "hf":
            # New Hugging Face router endpoint: router.huggingface.co (per current docs)
            api_url = f"https://router.huggingface.co/hf-inference/{provider['model']}"
            headers = {"Authorization": f"Bearer {provider['api_key']}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 1024, "temperature": 0.7},
            }
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    item = data[0]
                    if isinstance(item, dict) and "generated_text" in item:
                        text = item["generated_text"]
                        # Elimina promptul din raspuns daca e inclus
                        if text.startswith(prompt[:50]):
                            text = text[len(prompt):].strip()
                        return text
                elif isinstance(data, dict) and "generated_text" in data:
                    return data["generated_text"]
            raise Exception(f"HF error: {response.status_code} - {response.text[:200]}")

        return ""


# Global singleton for reuse
_fallback_llm: Optional[FallbackLLM] = None


def get_fallback_llm() -> FallbackLLM:
    global _fallback_llm
    if _fallback_llm is None:
        _fallback_llm = FallbackLLM()
    return _fallback_llm


if __name__ == "__main__":
    llm = FallbackLLM()
    response, used = llm.generate("Explain in simple terms what a fallback is in programming.")
    print(f"\nResponse from {used}:\n{response}")
