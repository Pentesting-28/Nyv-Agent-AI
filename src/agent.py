import os
import json
import re
from pprint import pprint
from .models.agent_model import AgentModel
from .tools import get_all_tools

class Agent(AgentModel):
    def __init__(self):
        self.tools = get_all_tools()
        self.tools_map = {tool.name: tool for tool in self.tools}
        self.system_prompt = self._build_system_prompt()

        # Initialize messages with system prompt
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _build_system_prompt(self) -> str:
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

    # Keep the abstract method implementation
    async def build_system_prompt(self) -> str:
        return self.system_prompt
        
    async def process_response(self, response):
        """
        Process the response from the AI.
        Parses tool calls from JSON blocks and executes them.
        """
        # Handle None or invalid responses
        if response is None:
            print("[Error: No response from API]")
            return False
            
        if not response.get("choices"):
            print("[Error: No choices in response]")
            return False
        
        response_message = response["choices"][0]["message"]
        content = response_message.get("content", "")
        
        # Add assistant message to history
        self.messages.append({"role": "assistant", "content": content})
        
        # Try to extract JSON tool call from the response
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        
        if json_match:
            try:
                tool_call = json.loads(json_match.group(1))
                tool_name = tool_call.get("tool")
                tool_args = tool_call.get("args", {})
                
                # Get the tool from our map
                tool = self.tools_map.get(tool_name)
                
                if tool:
                    print(f"[Executing tool: {tool_name}]")
                    
                    # Execute the tool
                    if isinstance(tool_args, dict):
                        result = await tool.execute(**tool_args)
                    else:
                        result = await tool.execute(tool_args)
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "user",
                        "content": f"Tool Output ({tool_name}):\n{result}"
                    })
                    
                    # Return True to continue the loop and get AI's response to the tool output
                    return True
                else:
                    print(f"[Error: Tool '{tool_name}' not found]")
                    
            except json.JSONDecodeError as e:
                print(f"[Error parsing tool JSON: {e}]")
        
        # No tool call found, just print the response
        print(f"Assistant: {content}")
        return False