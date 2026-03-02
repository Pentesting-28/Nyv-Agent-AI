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
        
        # 1. Try to extract JSON tool call from the response (standard JSON block)
        json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content)
        
        # 2. Try to extract raw JSON if no code fences
        if not json_match:
            json_match = re.search(r'(\{\s*"tool"\s*:\s*"[^"]+"\s*,\s*"args"\s*:\s*\{[\s\S]*?\}\s*\})', content)
        
        # 3. Try to extract K2-Think / Moonshot special format: <|tool_call_start|>[tool_name(arg1=val1, ...)]<|tool_call_end|>
        k2_match = re.search(r'<\|tool_call_start\|>\[(\w+)\(([\s\S]*?)\)\]<\|tool_call_end\|>', content)
        
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
                return await self._execute_tool_dto(tool_call_dto, content)

            except json.JSONDecodeError as e:
                console_ui.display_error(f"Error parsing tool JSON: {e}\nContent: {content[:100]}...")

        elif k2_match:
            tool_name = k2_match.group(1)
            args_str = k2_match.group(2)
            
            # Simple parser for "arg1=val1, arg2=val2"
            args = {}
            if args_str.strip():
                # This is a bit naive but handles basic cases
                # For complex cases we might need a better parser
                pairs = re.findall(r'(\w+)\s*=\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^,]+)', args_str)
                for key, val in pairs:
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    args[key] = val
            
            tool_call_dto = ToolCallDTO(
                id="call_" + str(len(self.messages)),
                name=tool_name,
                arguments=args
            )
            return await self._execute_tool_dto(tool_call_dto, content)

        console_ui.display_response(content)
        return False

    async def _execute_tool_dto(self, tool_call_dto: ToolCallDTO, full_content: str) -> bool:
        """Helper to execute a tool from a DTO and handle the response."""
        tool = self.tool_registry.get_tool(tool_call_dto.name)
        
        if tool:
            console_ui.display_tool_execution(tool_call_dto.name)
            
            # Parameter mapping for resilience (e.g., file_path -> path)
            args = tool_call_dto.arguments
            if isinstance(args, dict):
                # If tool expects 'path' but we got 'file_path' or 'filepath'
                if 'path' in tool.parameters.get('properties', {}) and 'path' not in args:
                    if 'file_path' in args:
                        args['path'] = args.pop('file_path')
                    elif 'filepath' in args:
                        args['path'] = args.pop('filepath')
            
            try:
                if isinstance(args, dict):
                    result = await tool.execute(**args)
                else:
                    result = await tool.execute(args)
                
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
            except Exception as e:
                console_ui.display_error(f"Error executing tool '{tool_call_dto.name}': {str(e)}")
                return False
        else:
            console_ui.display_error(f"Tool '{tool_call_dto.name}' not found")
            console_ui.display_response(full_content)
            return False
