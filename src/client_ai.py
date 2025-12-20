import httpx
import traceback
from typing import List, Optional
from ._types import NotGiven, not_given, Timeout
from ._constants import DEFAULT_MAX_RETRIES
from . import console_ui

class ClientAI:
    def __init__(
        self,
        api_key,
        base_url,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    async def chat_completions_create(
        self,
        model: str,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: Optional[float | Timeout | None | NotGiven] = not_given
    ):
        
        if timeout is not not_given:
            self.timeout = timeout
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        url = f"{self.base_url}/chat/completions"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    # Debug info for non-200 responses
                    console_ui.display_debug(
                        title="API Error Response",
                        data={
                            "status_code": response.status_code,
                            "url": url,
                            "model": model,
                            "response_text": response.text[:500] if response.text else "Empty response"
                        }
                    )
                    return None
                
                return response.json()
                
        except httpx.ConnectError as e:
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