"""
Model Fetcher Module
Fetches available free models from the OpenRouter API and filters
out models that are known to be non-functional.
"""

import httpx
from typing import List, Dict, Any
from datetime import datetime, timezone

from ..core.config import (
    OPENROUTER_MODELS_URL,
    MODEL_FETCH_TIMEOUT,
    MIN_RPM_THRESHOLD,
    DEPRECATION_GRACE_DAYS,
    FALLBACK_MODEL,
)


def _is_model_usable(model: dict) -> bool:
    """
    Determine if a model is usable based on its endpoint metadata.
    
    Filters out models that:
    - Have no endpoint data
    - Don't have a :free variant slug
    - Require content moderation (causes 404 for free keys)
    - Are disabled or hidden
    - Have a past deprecation date
    - Have RPM limits below our threshold (causes constant 429)
    - Don't support tool parameters (useless for our agent)
    """
    endpoint = model.get("endpoint")
    if not endpoint:
        return False

    variant_slug = endpoint.get("model_variant_slug", "")
    if not variant_slug or ":free" not in variant_slug:
        return False

    # Filter: moderation_required → 404 for free API keys
    if endpoint.get("moderation_required", False):
        return False

    # Filter: disabled or hidden models
    if endpoint.get("is_disabled", False) or endpoint.get("is_hidden", False):
        return False

    # Filter: deranked models (deprioritized by provider)
    if endpoint.get("is_deranked", False):
        return False

    # Filter: deprecated models (past or near-future deprecation)
    deprecation = endpoint.get("deprecation_date")
    if deprecation:
        try:
            dep_date = datetime.fromisoformat(deprecation)
            now = datetime.now(timezone.utc)
            # Make both timezone-aware for comparison
            if dep_date.tzinfo is None:
                dep_date = dep_date.replace(tzinfo=timezone.utc)
            # Skip if deprecated or within grace period
            if (dep_date - now).days < DEPRECATION_GRACE_DAYS:
                return False
        except (ValueError, TypeError):
            pass

    # Filter: very low RPM limits → constant rate limiting
    limit_rpm = endpoint.get("limit_rpm")
    if limit_rpm is not None and limit_rpm < MIN_RPM_THRESHOLD:
        return False

    # Filter: must support tool parameters for our agent
    if not endpoint.get("supports_tool_parameters", False):
        return False

    return True


def _score_model(model_dict: dict) -> tuple:
    """
    Generate a sort key for models. Higher score = listed first.
    
    Priority order:
    1. Supports reasoning (bonus for smarter models)
    2. Context length (larger = more capable)
    """
    supports_reasoning = 1 if model_dict.get("supports_reasoning", False) else 0
    context = model_dict.get("context_length", 0)
    
    return (supports_reasoning, context)


async def fetch_free_models(timeout: float = MODEL_FETCH_TIMEOUT) -> List[Dict[str, Any]]:
    """
    Fetch available free models from the OpenRouter API.
    
    Filters out non-functional models and sorts by capability.
    
    Returns:
        List of dicts with keys: name, model_id, context_length, supports_tools,
        supports_reasoning, author
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                OPENROUTER_MODELS_URL,
                params={"q": "free"}
            )
            response.raise_for_status()
            data = response.json()

        models = []
        raw_models = data.get("data", {}).get("models", [])

        for model in raw_models:
            if not _is_model_usable(model):
                continue

            endpoint = model.get("endpoint", {})

            models.append({
                "name": model.get("short_name", model.get("name", "Unknown")),
                "model_id": endpoint.get("model_variant_slug", ""),
                "context_length": model.get("context_length", 0),
                "supports_tools": True,  # Already filtered for this
                "supports_reasoning": model.get("supports_reasoning", False),
                "author": model.get("author", "unknown"),
            })

        # Sort: reasoning models first, then by context_length descending
        models.sort(key=_score_model, reverse=True)

        if not models:
            return [FALLBACK_MODEL]

        return models

    except Exception:
        # Network error, timeout, or parsing error → return fallback
        return [FALLBACK_MODEL]
