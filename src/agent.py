import os
import json
from pprint import pprint
from models.agent_model import AgentModel
from tools import get_all_tools


class Agent(AgentModel):
    def __init__(self):
        self.tools = get_all_tools()
        self.tools_map = {tool.name: tool for tool in self.tools}
        self.messages = []

    async def build_system_prompt(self):
        """
        Build system prompt with tool descriptions.
        Dynamically generates the prompt based on registered tools.
        """
        # Generate tool descriptions from registered tools
        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" 
            for tool in self.tools
        )
        
        return f"""You are a helpful AI assistant with access to tools.

Available tools:
{tool_descriptions}

To use a tool, you MUST respond with a JSON block inside markdown code fences, like this:
```json
{{
  "tool": "tool_name",
  "args": {{
    "parameter": "value"
  }}
}}
```

IMPORTANT:
1. After receiving a Tool Output, use that information to FULFILL the user's request.
2. Do not just describe the tool output unless asked.
3. Use tools when they can help answer the question.
4. Be conversational and friendly.
5. If you don't need a tool to answer, respond directly.

Example:
User: "Search for information about Python"
Assistant: ```json
{{
  "tool": "web_search",
  "args": {{
    "query": "Python programming language"
  }}
}}
```
"""
        
    async def process_response(self, response):
        """
        Process the response from the AI.
        Parses tool calls from JSON blocks and executes them.
        """
        if not response.get("choices"):
            return False
        
        response_message = response
        pprint(response_message)

        # TODO: Implement JSON block parsing for tool calls
        # Example:
        # content = response_message.get("content", "")
        # Parse ```json blocks to extract tool calls
        # Execute tools using self.tools_map
    
        return False