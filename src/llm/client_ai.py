import httpx
import asyncio
import traceback
from typing import List, Optional, Dict, Any
from .._types import NotGiven, not_given, Timeout
from ..core.config import DEFAULT_MAX_RETRIES, RETRYABLE_STATUS_CODES, BASE_RETRY_DELAY
from .. import console_ui
from ..core.base import LLMClient


class ClientAI(LLMClient):
    def __init__(
        self,
        api_key,
        base_url,
        model: str = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: Optional[float | Timeout | None | NotGiven] = not_given
    ) -> Any:
        
        if timeout is not not_given:
            self.timeout = timeout
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/chat/completions"

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url=url,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )

                    if response.status_code == 200:
                        return response.json()

                    # Check if this is a retryable error
                    if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                        delay = self._get_retry_delay(response, attempt)
                        console_ui.display_info(
                            f"Rate limited (429). Retrying in {delay:.0f}s... "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(delay)
                        continue

                    # Non-retryable error or last attempt
                    console_ui.display_debug(
                        title="API Error Response",
                        data={
                            "status_code": response.status_code,
                            "url": url,
                            "model": self.model,
                            "response_text": response.text[:500] if response.text else "Empty response"
                        }
                    )
                    return None
                    
            except httpx.ConnectError as e:
                if attempt < self.max_retries:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    console_ui.display_info(
                        f"Connection error. Retrying in {delay:.0f}s... "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)
                    continue
                    
                console_ui.display_debug(
                    title="Connection Error",
                    data={
                        "error_type": type(e).__name__,
                        "message": str(e),
                        "url": url,
                        "base_url": self.base_url
                    }
                )
                return None
                
            except httpx.TimeoutException as e:
                if attempt < self.max_retries:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    console_ui.display_info(
                        f"Timeout. Retrying in {delay:.0f}s... "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(delay)
                    continue
                    
                console_ui.display_debug(
                    title="Timeout Error",
                    data={
                        "error_type": type(e).__name__,
                        "message": str(e),
                        "url": url,
                        "timeout": self.timeout
                    }
                )
                return None
                
            except Exception as e:
                console_ui.display_debug(
                    title="Unexpected Error",
                    data={
                        "error_type": type(e).__name__,
                        "message": str(e),
                        "url": url,
                        "traceback": traceback.format_exc()
                    }
                )
                return None

        return None

    def _get_retry_delay(self, response: httpx.Response, attempt: int) -> float:
        """
        Calculate retry delay. Uses Retry-After header if present,
        otherwise uses exponential backoff: 2s, 4s, 8s...
        """
        retry_after = response.headers.get("retry-after")
        if retry_after:
            try:
                return float(retry_after)
            except (ValueError, TypeError):
                pass
        return BASE_RETRY_DELAY * (2 ** attempt)