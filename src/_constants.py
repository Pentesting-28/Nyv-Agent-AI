"""
Legacy constants module — re-exports from core.config for backward compatibility.
All new code should import directly from src.core.config.
"""

from .core.config import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_CONNECTION_LIMITS,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
)
