
"""Centralized Gemini Interactions API integration for Flarre-Fuzz."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

DEFAULT_MODEL = "gemini-3.8-flash"


def model() -> str:
    return os.getenv("FLARRE_MODEL", DEFAULT_MODEL)


def configured() -> bool:
    return (
        bool(os.getenv("GEMINI_API_KEY"))
        and not os.getenv("FLARRE_NO_LLM")
    )


def complete(prompt: str, max_tokens: int = 2500) -> str:
    if os.getenv("FLARRE_NO_LLM"):
        raise RuntimeError("LLM disabled (FLARRE_NO_LLM is set)")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    interaction = client.interactions.create(
        model=model(),
        input=prompt,
        timeout=180,
    )

    response_text = interaction.output_text

    if not response_text:
        raise RuntimeError("Gemini returned an empty response")

    return response_text


def describe(e: Exception) -> str:
    return f"{type(e).__name__}: {str(e)[:200]}"
