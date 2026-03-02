import pytest
import asyncio
from typing import List, Dict, Any, Optional
from src.core.base import LLMClient, BaseTool
from src.core.registry import ToolRegistry
from src.schemas.dtos import MessageDTO

class MockLLMClient(LLMClient):
    """A mock LLM client for testing purposes."""
    def __init__(self):
        self.responses = []
        self.last_messages = []

    def add_response(self, content: str = "", tool_calls: Optional[List[Dict[str, Any]]] = None):
        """Adds a response to the queue."""
        response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                }
            }]
        }
        if tool_calls:
            # We add it as content because our agent parses from content string
            # if we simulate the raw content response.
            # However, standard OpenAI response might have it in tool_calls field.
            # But our agent currently parses 'content' via regex.
            pass
        self.responses.append(response)

    async def chat_completion(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        self.last_messages = messages
        if self.responses:
            return self.responses.pop(0)
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Default mock response"
                }
            }]
        }

class DummyTool(BaseTool):
    """A simple tool for testing the registry and agent."""
    def __init__(self):
        super().__init__(
            name="dummy_tool",
            description="A tool that returns what you give it.",
            parameters={
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                },
                "required": ["input"]
            }
        )

    async def execute(self, input: str) -> str:
        return f"Processed: {input}"

@pytest.fixture
def tool_registry():
    registry = ToolRegistry()
    registry.register_tool(DummyTool())
    return registry

@pytest.fixture
def mock_llm_client():
    return MockLLMClient()
