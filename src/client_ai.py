import httpx
from typing import List, Optional
from ._types import NotGiven, not_given, Timeout
from ._constants import DEFAULT_MAX_RETRIES

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

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    raise Exception(f"Error: {response.status_code}")
                
                return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        
        
    



        