import pytest
import httpx
from src.llm.client_ai import ClientAI

@pytest.mark.asyncio
async def test_client_ai_chat_completion(mocker):
    # Mock httpx.AsyncClient.post
    mock_post = mocker.patch("httpx.AsyncClient.post")
    
    # Mock response object
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    mock_post.return_value = mock_response
    
    client = ClientAI(api_key="test_key", base_url="https://api.test")
    messages = [{"role": "user", "content": "Hello"}]
    
    result = await client.chat_completion(messages)
    
    # Verify post was called with correct data
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test_key"
    assert kwargs["json"]["model"] == client.model
    assert kwargs["json"]["messages"] == messages
    
    assert result["choices"][0]["message"]["content"] == "Test response"

@pytest.mark.asyncio
async def test_client_ai_with_tools(mocker):
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": []}
    mock_post.return_value = mock_response
    
    client = ClientAI(api_key="test_key", base_url="https://api.test")
    tools = [{"type": "function", "function": {"name": "test"}}]
    
    await client.chat_completion(messages=[], tools=tools)
    
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["tools"] == tools
