from typing import Dict, List, Any
from .base import BaseTool

class ToolRegistry:
    """Registry to manage and discover tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    def get_tools_definitions(self) -> List[Dict[str, Any]]:
        return [tool.to_dict() for tool in self._tools.values()]
