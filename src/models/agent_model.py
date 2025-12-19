"""
Agent Model Module
Defines the base class for all agent models.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class AgentModel(ABC):
    """Base class for all agent models."""

    @abstractmethod
    async def build_system_prompt(self, **kwargs) -> str:
        """
        Build the system prompt for the agent.
        Must be implemented by subclasses.
        
        Returns:
            A string result that can be sent back to the AI
        """
        pass

    async def process_response(self, response: Dict[str, Any]):
        """
        Process the response from the AI.
        Must be implemented by subclasses.
        
        Returns:
            A boolean result that indicates if the response was processed successfully
        """
        pass
    
