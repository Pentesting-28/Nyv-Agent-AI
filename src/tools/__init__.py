"""
Tools Module
Exports all available tools for the AI agent.
"""

from src.models.function_model import BaseTool, ToolRegistry, tool_registry

# Import tools to register them in the registry
# Import tools to register them in the registry
from src.tools.web_search import web_search_tool, WebSearchTool, web_navigate_tool, WebNavigateTool
from src.tools.file_system import (
    list_directory_tool, ListDirectoryTool,
    read_file_tool, ReadFileTool,
    write_file_tool, WriteFileTool,
    make_directory_tool, MakeDirectoryTool,
    delete_tool, DeleteTool,
    move_tool, MoveTool,
    copy_tool, CopyTool,
    get_file_info_tool, GetFileInfoTool,
    search_files_tool, SearchFilesTool,
    append_file_tool, AppendFileTool,
    batch_move_tool, BatchMoveTool
)


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
    "web_navigate_tool",
    "list_directory_tool",
    "read_file_tool",
    "write_file_tool",
    "make_directory_tool",
    "delete_tool",
    "move_tool",
    "copy_tool",
    "get_file_info_tool",
    "search_files_tool",
    "append_file_tool",
    "batch_move_tool",
    # Tool classes
    "WebSearchTool",
    "WebNavigateTool",
    "ListDirectoryTool",
    "ReadFileTool",
    "WriteFileTool",
    "MakeDirectoryTool",
    "DeleteTool",
    "MoveTool",
    "CopyTool",
    "GetFileInfoTool",
    "SearchFilesTool",
    "AppendFileTool",
    "BatchMoveTool",
    # Helper functions
    "get_all_tools",
    "get_all_schemas",
    "get_tool",
]
