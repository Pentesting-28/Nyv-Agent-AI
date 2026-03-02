"""Tests for the model_fetcher module."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.llm.model_fetcher import fetch_free_models, FALLBACK_MODEL, _is_model_usable


def _make_model(slug="test/model", variant="test/model:free",
                tools=True, moderation=False, disabled=False,
                hidden=False, deranked=False, deprecation=None,
                rpm=50, context=128000):
    """Helper to build a minimal model dict for testing."""
    return {
        "slug": slug,
        "name": f"Test: {slug} (free)",
        "short_name": f"{slug} (free)",
        "author": slug.split("/")[0],
        "context_length": context,
        "supports_reasoning": False,
        "endpoint": {
            "model_variant_slug": variant,
            "supports_tool_parameters": tools,
            "moderation_required": moderation,
            "is_disabled": disabled,
            "is_hidden": hidden,
            "is_deranked": deranked,
            "deprecation_date": deprecation,
            "limit_rpm": rpm,
        }
    }


# --- _is_model_usable unit tests ---

def test_usable_model():
    assert _is_model_usable(_make_model()) is True


def test_filter_moderation_required():
    assert _is_model_usable(_make_model(moderation=True)) is False


def test_filter_disabled():
    assert _is_model_usable(_make_model(disabled=True)) is False


def test_filter_deranked():
    assert _is_model_usable(_make_model(deranked=True)) is False


def test_filter_no_tools():
    assert _is_model_usable(_make_model(tools=False)) is False


def test_filter_low_rpm():
    assert _is_model_usable(_make_model(rpm=5)) is False


def test_filter_deprecated():
    assert _is_model_usable(_make_model(deprecation="2020-01-01")) is False


def test_allow_future_deprecation():
    assert _is_model_usable(_make_model(deprecation="2099-12-31")) is True


def test_filter_no_free_variant():
    assert _is_model_usable(_make_model(variant="test/model:paid")) is False


# --- fetch_free_models integration tests ---

MOCK_API_RESPONSE = {
    "data": {
        "models": [
            _make_model("org/good", "org/good:free", context=128000),
            _make_model("org/bad-mod", "org/bad-mod:free", moderation=True),
            _make_model("org/small", "org/small:free", context=32000),
        ]
    }
}


@pytest.mark.asyncio
async def test_fetch_filters_and_sorts():
    """Should filter bad models and sort by context descending."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch("src.llm.model_fetcher.httpx.AsyncClient") as MockClient:
        inst = AsyncMock()
        inst.get.return_value = mock_response
        inst.__aenter__ = AsyncMock(return_value=inst)
        inst.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = inst

        models = await fetch_free_models()

    # bad-mod should be filtered out
    assert len(models) == 2
    # Sorted by context descending
    assert models[0]["context_length"] == 128000
    assert models[1]["context_length"] == 32000


@pytest.mark.asyncio
async def test_fetch_network_error_returns_fallback():
    """Should return fallback model on network failure."""
    with patch("src.llm.model_fetcher.httpx.AsyncClient") as MockClient:
        inst = AsyncMock()
        inst.get.side_effect = Exception("Connection refused")
        inst.__aenter__ = AsyncMock(return_value=inst)
        inst.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = inst

        models = await fetch_free_models()

    assert len(models) == 1
    assert models[0]["model_id"] == FALLBACK_MODEL["model_id"]


@pytest.mark.asyncio
async def test_fetch_empty_returns_fallback():
    """Should return fallback when all models are filtered out."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"models": []}}
    mock_response.raise_for_status = MagicMock()

    with patch("src.llm.model_fetcher.httpx.AsyncClient") as MockClient:
        inst = AsyncMock()
        inst.get.return_value = mock_response
        inst.__aenter__ = AsyncMock(return_value=inst)
        inst.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = inst

        models = await fetch_free_models()

    assert len(models) == 1
    assert models[0] == FALLBACK_MODEL

def test_filter_deprecation_grace_period():
    """Verify models deprecated within 7 days are filtered out."""
    from datetime import datetime, timedelta
    
    # Deprecated yesterday (should be filtered)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    assert _is_model_usable(_make_model(deprecation=yesterday)) is False
    
    # Deprecated 5 days ago (should be filtered)
    five_days_ago = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    assert _is_model_usable(_make_model(deprecation=five_days_ago)) is False
    
    # Deprecated 10 days ago (definitely filtered)
    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    assert _is_model_usable(_make_model(deprecation=ten_days_ago)) is False

@pytest.mark.asyncio
async def test_sorting_prioritizes_reasoning():
    """Verify models with reasoning support are prioritized."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    # Lower context but supports reasoning vs Higher context no reasoning
    mock_response.json.return_value = {
        "data": {
            "models": [
                _make_model("org/high-ctx", "org/high-ctx:free", context=200000),
                {**_make_model("org/reasoning", "org/reasoning:free", context=128000), "supports_reasoning": True}
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()

    with patch("src.llm.model_fetcher.httpx.AsyncClient") as MockClient:
        inst = AsyncMock()
        inst.get.return_value = mock_response
        inst.__aenter__ = AsyncMock(return_value=inst)
        inst.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = inst

        models = await fetch_free_models()

    # reasoning model should be first despite lower context
    assert models[0]["model_id"] == "org/reasoning:free"
    assert models[1]["model_id"] == "org/high-ctx:free"
