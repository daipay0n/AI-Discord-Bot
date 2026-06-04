import logging
import os
import random
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
CHAT_ENDPOINT = f"{OPENROUTER_API_BASE}/chat/completions"
MODELS_ENDPOINT = f"{OPENROUTER_API_BASE}/models"

SKIP_STATUS_CODES = {429, 502, 503}

_free_models: list[str] = []


async def fetch_free_models() -> list[str]:
    global _free_models
    api_key = os.environ["OPENROUTER_API_KEY"].strip()
    logger.debug("Fetching free models from OpenRouter (key prefix: %s)", api_key[:12])
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            MODELS_ENDPOINT,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        resp.raise_for_status()
        data = resp.json()

    models = [m["id"] for m in data.get("data", []) if m["id"].endswith(":free")]
    logger.info("Found %d free models on OpenRouter", len(models))
    _free_models = models
    return models


def _pick_preferred(free_models: list[str], hint: str) -> Optional[str]:
    hint_lower = hint.lower()
    for m in free_models:
        if hint_lower in m.lower():
            return m
    return free_models[0] if free_models else None


def _build_fallback_queue(preferred: Optional[str], free_models: list[str]) -> list[str]:
    rest = [m for m in free_models if m != preferred]
    random.shuffle(rest)
    if preferred:
        return [preferred] + rest
    return rest


async def chat_completion(
    messages: list[dict],
    preferred_model: Optional[str] = None,
) -> Optional[str]:
    api_key = os.environ["OPENROUTER_API_KEY"].strip()
    logger.debug("API key prefix: %s", api_key[:12])

    free_models = _free_models or await fetch_free_models()
    if not free_models:
        logger.error("No free models available from OpenRouter")
        return None

    preferred = preferred_model or (free_models[0] if free_models else None)
    queue = _build_fallback_queue(preferred, free_models)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://replit.com",
        "X-Title": "Discord AI Agent",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        for model in queue:
            payload = {
                "model": model,
                "messages": messages,
            }
            try:
                logger.debug("Trying model: %s", model)
                resp = await client.post(CHAT_ENDPOINT, json=payload, headers=headers)

                if resp.status_code == 404:
                    logger.debug("Model not found, skipping: %s", model)
                    continue

                if resp.status_code in SKIP_STATUS_CODES:
                    logger.debug(
                        "Received %d from model %s, skipping", resp.status_code, model
                    )
                    continue

                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                logger.debug("Got response from model: %s", model)
                return content

            except httpx.TimeoutException:
                logger.debug("Timeout on model %s, skipping", model)
                continue
            except httpx.HTTPStatusError as e:
                logger.debug("HTTP error %d on model %s: %s", e.response.status_code, model, e)
                continue
            except Exception as e:
                logger.debug("Unexpected error on model %s: %s", model, e)
                continue

    logger.error("All %d free models exhausted, returning None", len(queue))
    return None
