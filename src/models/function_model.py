"""
Function Model Module
Defines the base class for all tools that the AI agent can use.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable

class BaseTool(ABC):
    """
    Base class for creating tools that can be used by the AI agent.
    Each tool must implement the 'execute' method.
    """
    
    def __init__(self, name: str, description: str, parameters: Optional[Dict] = None):
        """
        Initialize a tool.
        
        Args:
            name: The name of the tool (used by the AI to call it)
            description: A clear description of what the tool does
            parameters: JSON schema for the tool's parameters
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        Execute the tool with the given arguments.
        Must be implemented by subclasses.
        
        Returns:
            A string result that can be sent back to the AI
        """
        pass
    
    def to_schema(self) -> Dict[str, Any]:
        """
        Convert the tool to OpenAI's function calling schema format.
        
        Returns:
            A dictionary in the OpenAI tool format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"


class ToolRegistry:
    """
    Registry to manage all available tools.
    Provides methods to register, retrieve, and list tools.
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all(self) -> List[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas in OpenAI format."""
        return [tool.to_schema() for tool in self._tools.values()]
    
    def get_available_functions(self) -> Dict[str, Callable]:
        """
        Get a dictionary mapping tool names to their execute methods.
        Useful for the agent's process_response method.
        """
        return {name: tool.execute for name, tool in self._tools.items()}
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __repr__(self) -> str:
        return f"<ToolRegistry: {len(self)} tools>"


# Global registry instance
tool_registry = ToolRegistry()
