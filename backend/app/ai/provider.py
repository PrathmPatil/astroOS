"""AI provider adapter (OpenAI / Ollama / rule-based fallback)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.ai.prompts import build_prompt, rule_based_fallback
from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def generate_analysis(
    language: str,
    focus: str,
    chart_summary: dict[str, Any],
) -> tuple[str, str]:
    """Return (analysis_text, provider_name)."""
    settings = get_settings()
    system, user = build_prompt(language, focus, chart_summary)

    if settings.ai_provider == "none":
        return rule_based_fallback(language, focus, chart_summary), "rule_engine"

    if settings.ai_provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": settings.ollama_model,
                        "stream": False,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("message", {}).get("content")
                    if content:
                        return content, f"ollama:{settings.ollama_model}"
        except Exception as exc:  # noqa: BLE001
            logger.warning("Ollama unavailable: %s", exc)

    if settings.ai_provider == "openai" and settings.openai_api_key:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.openai_api_key)
            completion = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.4,
            )
            content = completion.choices[0].message.content or ""
            if content:
                return content, f"openai:{settings.openai_model}"
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI unavailable: %s", exc)

    return rule_based_fallback(language, focus, chart_summary), "rule_engine_fallback"
