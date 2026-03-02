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

@pytest.mark.asyncio
async def test_client_ai_retry_on_429(mocker):
    """Verify that the client retries on 429 status code."""
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_sleep = mocker.patch("asyncio.sleep", return_value=None)
    
    # First response is 429, second is 200
    mock_resp_429 = mocker.MagicMock()
    mock_resp_429.status_code = 429
    mock_resp_429.headers = {}
    
    mock_resp_200 = mocker.MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {"choices": [{"message": {"content": "Success"}}]}
    
    mock_post.side_effect = [mock_resp_429, mock_resp_200]
    
    client = ClientAI(api_key="key", base_url="url", max_retries=2)
    result = await client.chat_completion(messages=[])
    
    assert mock_post.call_count == 2
    assert mock_sleep.call_count == 1
    assert result["choices"][0]["message"]["content"] == "Success"

@pytest.mark.asyncio
async def test_client_ai_respects_retry_after(mocker):
    """Verify that the client respects the Retry-After header."""
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_sleep = mocker.patch("asyncio.sleep", return_value=None)
    
    mock_resp_429 = mocker.MagicMock()
    mock_resp_429.status_code = 429
    mock_resp_429.headers = {"retry-after": "10"}
    
    mock_resp_200 = mocker.MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {"choices": []}
    
    mock_post.side_effect = [mock_resp_429, mock_resp_200]
    
    client = ClientAI(api_key="key", base_url="url")
    await client.chat_completion(messages=[])
    
    # Verify sleep was called with 10 seconds from header
    mock_sleep.assert_called_once_with(10.0)

@pytest.mark.asyncio
async def test_client_ai_retry_on_connection_error(mocker):
    """Verify that the client retries on connection errors."""
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mocker.patch("asyncio.sleep", return_value=None)
    
    import httpx
    mock_resp_200 = mocker.MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {"choices": []}
    
    # Exception followed by success
    mock_post.side_effect = [httpx.ConnectError("Network down"), mock_resp_200]
    
    client = ClientAI(api_key="key", base_url="url", max_retries=1)
    await client.chat_completion(messages=[])
    
    assert mock_post.call_count == 2

@pytest.mark.asyncio
async def test_client_ai_max_retries_exceeded(mocker):
    """Verify that the client returns None when retries are exhausted."""
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mocker.patch("asyncio.sleep", return_value=None)
    
    mock_resp_429 = mocker.MagicMock()
    mock_resp_429.status_code = 429
    mock_resp_429.headers = {}
    
    # Always return 429
    mock_post.return_value = mock_resp_429
    
    client = ClientAI(api_key="key", base_url="url", max_retries=2)
    result = await client.chat_completion(messages=[])
    
    assert mock_post.call_count == 3  # Initial + 2 retries
    assert result is None
