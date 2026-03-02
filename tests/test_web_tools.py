import pytest
import httpx
from src.tools.web_search import WebSearchTool, WebNavigateTool

@pytest.mark.asyncio
async def test_web_search_tool(mocker):
    # Mock httpx.AsyncClient.post
    mock_post = mocker.patch("httpx.AsyncClient.post")
    
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    # Snippet of DuckDuckGo HTML
    mock_response.text = """
    <div class="result">
        <a class="result__a" href="https://example.com/uddg=https%3A%2F%2Factual-site.com">Example Title</a>
        <a class="result__snippet">This is a test snippet.</a>
    </div>
    """
    mock_post.return_value = mock_response
    
    tool = WebSearchTool()
    result = await tool.execute(query="test query", max_results=1)
    
    assert "actual-site.com" in result
    assert "Example Title" in result
    assert "This is a test snippet" in result

@pytest.mark.asyncio
async def test_visit_url_tool(mocker):
    # Mock httpx.AsyncClient.get
    mock_get = mocker.patch("httpx.AsyncClient.get")
    
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.text = "# Page Content\nThis is markdown."
    mock_get.return_value = mock_response
    
    tool = WebNavigateTool()
    result = await tool.execute(url="https://example.com")
    
    assert "Page Content" in result
    assert "This is markdown" in result
    assert "via BrowserFly" in result
