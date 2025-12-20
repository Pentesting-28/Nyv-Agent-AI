"""
Web Search Tool
Performs web searches using DuckDuckGo's HTML interface.
"""

import re
import httpx
from typing import Optional
from urllib.parse import unquote
from src.models.function_model import BaseTool, tool_registry


class WebSearchTool(BaseTool):

    BASE_URL = "https://html.duckduckgo.com/html/"
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://html.duckduckgo.com/",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    DEFAULT_TIMEOUT = 10.0
    DEFAULT_MAX_RESULTS = 5
    
    # Regex patterns (compiled once for performance)
    # Note: DDG's HTML has class before href, so we need a flexible pattern
    PATTERN_RESULTS = re.compile(r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>')
    PATTERN_SNIPPETS = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
    PATTERN_URL_EXTRACT = re.compile(r'uddg=([^&]+)')
    PATTERN_HTML_TAGS = re.compile(r'<[^>]+>')
    
    def __init__(self, region: str = "wt-wt"):
        """
        Initialize the web search tool.
        
        Args:
            region: Search region code (default: 'wt-wt' for global, 'es-es' for Spain)
        """
        super().__init__(
            name="web_search",
            description="Search the web for current information. Use this to find recent news, facts, or any information not in your training data. Input should be a search query.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 3, max: 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
        self.region = region
    
    def _extract_real_url(self, raw_url: str) -> str:
        """
        Extract the actual URL from DuckDuckGo's redirect URL.
        
        Args:
            raw_url: The raw URL from DuckDuckGo (may contain redirect)
            
        Returns:
            The cleaned, actual URL
        """
        if "uddg=" not in raw_url:
            return raw_url
        
        match = self.PATTERN_URL_EXTRACT.search(raw_url)
        if match:
            return unquote(match.group(1))
        return raw_url
    
    def _clean_html(self, text: str) -> str:
        """
        Remove HTML tags from text.
        
        Args:
            text: Text potentially containing HTML tags
            
        Returns:
            Clean text without HTML tags
        """
        return self.PATTERN_HTML_TAGS.sub('', text).strip()
    
    def _format_results(self, query: str, results: list, snippets: list, max_results: int) -> str:
        """
        Format search results into a readable string.
        
        Args:
            query: Original search query
            results: List of (url, title) tuples
            snippets: List of description snippets
            max_results: Maximum number of results to include
            
        Returns:
            Formatted string with search results
        """
        output_lines = [f"Search results for: '{query}'\n"]
        
        for i in range(min(len(results), max_results)):
            raw_link, title = results[i]
            description = snippets[i] if i < len(snippets) else "No description available."
            
            # Clean the data
            clean_url = self._extract_real_url(raw_link)
            clean_description = self._clean_html(description)
            
            output_lines.append(f"[{i + 1}] {title}")
            output_lines.append(f"    URL: {clean_url}")
            output_lines.append(f"    Description: {clean_description}\n")
        
        return "\n".join(output_lines)
    
    async def execute(self, query: str, max_results: Optional[int] = None) -> str:
        """
        Perform a web search and return formatted results.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return (1-10)
            
        Returns:
            Formatted string with search results or error message
        """
        print(f"[Tool] called: {self.name}")
        
        # Validate and set max_results
        if max_results is None:
            max_results = self.DEFAULT_MAX_RESULTS
        max_results = max(1, min(10, max_results))  # Clamp between 1 and 10
        
        # Validate query
        query = query.strip()
        if not query:
            return "Error: Search query cannot be empty."
        
        request_data = {
            "q": query,
            "kl": self.region,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(
                    self.BASE_URL,
                    data=request_data,
                    headers=self.DEFAULT_HEADERS
                )
                response.raise_for_status()
                html = response.text
            
            # Parse results
            results = self.PATTERN_RESULTS.findall(html)
            snippets = self.PATTERN_SNIPPETS.findall(html)
            
            if not results:
                return f"No results found for: '{query}'"
            
            return self._format_results(query, results, snippets, max_results)
        
        except httpx.TimeoutException:
            return "Error: Search request timed out. Please try again."
        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code} - Unable to complete search."
        except httpx.RequestError as e:
            return f"Error: Network error - {str(e)}"
        except Exception as e:
            return f"Error: Unexpected error during search - {str(e)}"


# Create and register the tool
web_search_tool = WebSearchTool(region="es-es")
tool_registry.register(web_search_tool)