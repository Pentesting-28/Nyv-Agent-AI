"""
Tools Module
Exports all available tools for the AI agent.
"""

from src.models.function_model import BaseTool, ToolRegistry, tool_registry

# Import tools to register them in the registry
from src.tools.web_search import web_search_tool, WebSearchTool


def get_all_tools():
    """Get all registered tools."""
    return tool_registry.get_all()


def get_all_schemas():
    """Get all tool schemas in OpenAI format."""
    return tool_registry.get_schemas()


def get_tool(name: str):
    """Get a specific tool by name."""
    return tool_registry.get(name)


__all__ = [
    # Base classes
    "BaseTool",
    "ToolRegistry",
    "tool_registry",
    # Tool instances
    "web_search_tool",
    # Tool classes
    "WebSearchTool",
    # Helper functions
    "get_all_tools",
    "get_all_schemas",
    "get_tool",
]
