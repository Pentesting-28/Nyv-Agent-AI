"""
Centralized Configuration Module
All application constants organized by domain.
"""

import httpx


# =============================================================================
# HTTP Client Defaults
# =============================================================================

DEFAULT_TIMEOUT = httpx.Timeout(timeout=600, connect=5.0)
DEFAULT_MAX_RETRIES = 3
APP_TIMEOUT = 120.0  # Default timeout for LLM calls in the app
DEFAULT_CONNECTION_LIMITS = httpx.Limits(
    max_connections=1000,
    max_keepalive_connections=100
)

# =============================================================================
# Retry Policy
# =============================================================================

INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
BASE_RETRY_DELAY = 2.0
RETRYABLE_STATUS_CODES = {429, 502, 503}

# =============================================================================
# OpenRouter / Model Fetcher
# =============================================================================

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/frontend/models/find"
MODEL_FETCH_TIMEOUT = 15.0
MIN_RPM_THRESHOLD = 10
DEPRECATION_GRACE_DAYS = 7

FALLBACK_MODEL = {
    "name": "Meta: Llama 3.3 70B Instruct (free)",
    "model_id": "meta-llama/llama-3.3-70b-instruct:free",
    "context_length": 128000,
    "supports_tools": True,
    "author": "meta-llama",
}

# =============================================================================
# Web Search (DuckDuckGo)
# =============================================================================

DUCKDUCKGO_BASE_URL = "https://html.duckduckgo.com/html/"
DUCKDUCKGO_TIMEOUT = 10.0
DUCKDUCKGO_MAX_RESULTS = 5
DUCKDUCKGO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
    "Referer": "https://html.duckduckgo.com/",
    "Content-Type": "application/x-www-form-urlencoded",
}

# =============================================================================
# BrowserFly (URL Renderer)
# =============================================================================

BROWSERFLY_API_URL = "https://browserflyio.vercel.app/api/markdown"
BROWSERFLY_TIMEOUT = 30.0

# =============================================================================
# UI / Console Settings
# =============================================================================

UI_THEME = {
    "info": "bold cyan",
    "warning": "bold yellow", 
    "error": "bold red",
    "success": "bold green",
    "tool": "bold magenta",
    "user_prompt": "bold green",
    "system": "dim white",
    "hacker_green": "bold #00ff00",
    "hacker_red": "bold #ff0000",
}

NYV_BANNER = r"""
                                _   _  __     __ __      __       _    ___ 
                                | \ | | \ \   / / \ \    / /      / \  |_ _|
                                |  \| |  \ \_/ /   \ \  / /      / _ \  | | 
                                | |\  |    | |      \ \/ /      / ___ \ | | 
                                |_| \_|    |_|       \__/      /_/   \_\___|
                                
                                                AGENT AI SYSTEM                              
                                                [bold red]SYSTEM: ONLINE[/bold red] ⚡
"""
