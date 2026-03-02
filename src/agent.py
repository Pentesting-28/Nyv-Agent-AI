import os
import json
import re
import ast
from typing import List, Dict, Any

from . import console_ui
from src.core.base import LLMClient
from src.core.registry import ToolRegistry
from src.schemas.dtos import MessageDTO, ToolCallDTO, ToolResultDTO

class Agent:
    def __init__(self, llm_client: LLMClient, tool_registry: ToolRegistry):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.system_prompt = self._build_system_prompt()

        # Initialize messages with system prompt
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _build_system_prompt(self) -> str:
        """
        Build system prompt with tool descriptions dynamically generated
        from registered tools.
        """
        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" 
            for tool in self.tool_registry.get_all_tools()
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
"""

    def add_message(self, message: MessageDTO):
        """Adds a message DTO to the agent's internal history."""
        self.messages.append(message.to_dict())

    async def run_cycle(self) -> bool:
        """
        Runs one cycle of the agent (completion + tool execution if needed).
        Returns True if a tool was called (meaning another cycle should run),
        or False if the turn is complete.
        """
        response = await self.llm_client.chat_completion(
            messages=self.messages
        )
        return await self.process_response(response)

    async def process_response(self, response) -> bool:
        """
        Process the response from the AI.
        Parses tool calls from JSON blocks and executes them.
        """
        if response is None:
            console_ui.display_error("No response from API")
            return False
            
        if not response.get("choices"):
            console_ui.display_error("No choices in response")
            return False
        
        response_message = response["choices"][0]["message"]
        content = response_message.get("content", "")
        
        # Add assistant message to history
        self.messages.append({"role": "assistant", "content": content})
        
        # Try to extract JSON tool call from the response
        json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content)
        
        if not json_match:
            json_match = re.search(r'(\{\s*"tool"\s*:\s*"[^"]+"\s*,\s*"args"\s*:\s*\{[\s\S]*?\}\s*\})', content)
        
        if json_match:
            try:
                json_str = json_match.group(1)
                
                # Clean up json strings (trailing commas, whitespace)
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                json_str = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                json_str = re.sub(r'\s+(?=[:,\]}\{])', '', json_str)
                json_str = re.sub(r'(?<=[:,\[\{])\s+', '', json_str)
                
                try:
                    tool_call_dict = json.loads(json_str)
                except json.JSONDecodeError as e:
                    try:
                        tool_call_dict = json.loads(json_str, strict=False)
                    except json.JSONDecodeError:
                        try:
                            tool_call_dict = ast.literal_eval(json_str)
                        except (ValueError, SyntaxError):
                            try:
                                cleaned_str = re.sub(r'[\x00-\x1f\x7f]', ' ', json_str)
                                cleaned_str = re.sub(r'(?<!%)\s+', ' ', cleaned_str)
                                cleaned_str = cleaned_str.replace('%', '%25')
                                tool_call_dict = json.loads(cleaned_str)
                            except json.JSONDecodeError:
                                console_ui.display_error(f"Cannot parse tool JSON: {str(e)}\nJSON: {json_str[:200]}...")
                                console_ui.display_response(content)
                                return False

                # Map extracted JSON to our standard DTO
                tool_call_dto = ToolCallDTO(
                    id="call_" + str(len(self.messages)),
                    name=tool_call_dict.get("tool", ""),
                    arguments=tool_call_dict.get("args", {})
                )
                
                tool = self.tool_registry.get_tool(tool_call_dto.name)
                
                if tool:
                    console_ui.display_tool_execution(tool_call_dto.name)
                    
                    if isinstance(tool_call_dto.arguments, dict):
                        result = await tool.execute(**tool_call_dto.arguments)
                    else:
                        result = await tool.execute(tool_call_dto.arguments)
                    
                    # Wrap execution result into DTO
                    tool_result = ToolResultDTO(
                        tool_call_id=tool_call_dto.id,
                        name=tool_call_dto.name,
                        content=str(result)
                    )
                    
                    console_ui.display_tool_result(tool_call_dto.name, tool_result.content)
                    
                    self.messages.append({
                        "role": "user",
                        "content": f"Tool Output ({tool_result.name}):\n{tool_result.content}"
                    })
                    
                    return True
                else:
                    console_ui.display_error(f"Tool '{tool_call_dto.name}' not found")
                    
            except json.JSONDecodeError as e:
                console_ui.display_error(f"Error parsing tool JSON: {e}\nContent: {content[:100]}...")
        
        console_ui.display_response(content)
        return False
