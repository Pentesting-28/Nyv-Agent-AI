
import os
import json
import re
import ast
from pprint import pprint
from .models.agent_model import AgentModel
from .tools import get_all_tools
from . import console_ui

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

WEB NAVIGATION NOTES:
- The visit_url tool uses BrowserFly API to render web pages and convert them to markdown
- The content returned is already formatted in markdown, making it easy to analyze
- BrowserFly handles JavaScript rendering, so dynamic content is included
- The markdown format preserves structure: headings, links, lists, and paragraphs
- You can directly analyze the markdown content without any HTML parsing

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

User: "Visit the Wikipedia article about Python"
Assistant: ```json
{{
  "tool": "visit_url",
  "args": {{
    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
  }}
}}
```
[Tool will fetch the page via BrowserFly and return markdown content]
"""

    # Keep the abstract method implementation
    async def build_system_prompt(self) -> str:
        return self.system_prompt
        
    async def process_response(self, response):
        """
        Process the response from the AI.
        Parses tool calls from JSON blocks and executes them.
        """
        # print(f"DATA API: {response}")
        # Handle None or invalid responses
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
        # Use a more robust pattern that handles nested braces
        json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content)
        
        # If first pattern fails, try alternative patterns
        if not json_match:
            # Try without code fences (some LLMs output raw JSON)
            json_match = re.search(r'(\{\s*"tool"\s*:\s*"[^"]+"\s*,\s*"args"\s*:\s*\{[\s\S]*?\}\s*\})', content)
        
        if json_match:
            try:
                json_str = json_match.group(1)
                
                # Note: We've disabled comment stripping as it was causing issues with URLs containing //
                # The JSON should be clean enough from the LLM without comment stripping
                # json_str = re.sub(r'(?<!\\)//[^\n]*', '', json_str)
                # json_str = re.sub(r'(?<!\\)/\*.*?\*/', '', json_str, flags=re.DOTALL)
                
                # Clean up trailing commas before closing braces (common LLM error)
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                
                # Normalize whitespace: replace newlines, tabs, carriage returns with spaces
                # This preserves JSON structure while removing problematic control characters
                json_str = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                # Remove multiple consecutive spaces, but be very conservative
                # Only remove spaces that are clearly outside of string values
                json_str = re.sub(r'\s+(?=[:,\]}\{])', '', json_str)  # Remove spaces before JSON structure chars
                json_str = re.sub(r'(?<=[:,\[\{])\s+', '', json_str)  # Remove spaces after JSON structure chars
                
                # Sanitize JSON string to handle common LLM errors
                try:
                    tool_call = json.loads(json_str)
                except json.JSONDecodeError as e:
                    # Fallback 1: Try with strict=False
                    try:
                        tool_call = json.loads(json_str, strict=False)
                    except json.JSONDecodeError:
                        # Fallback 2: Try ast.literal_eval for Python-style dicts (single quotes)
                        try:
                            tool_call = ast.literal_eval(json_str)
                        except (ValueError, SyntaxError):
                            # Last resort: remove control chars entirely and normalize whitespace
                            try:
                                # Remove control characters but preserve URL-encoded sequences
                                cleaned_str = re.sub(r'[\x00-\x1f\x7f]', ' ', json_str)
                                # Remove multiple spaces but preserve URL-encoded characters
                                cleaned_str = re.sub(r'(?<!%)\s+', ' ', cleaned_str)
                                # Fix common issues with URL encoding in JSON strings
                                cleaned_str = cleaned_str.replace('%', '%25')  # Double-encode to be safe
                                tool_call = json.loads(cleaned_str)
                            except json.JSONDecodeError:
                                # If all parsing fails, show the error and continue
                                console_ui.display_error(f"Cannot parse tool JSON: {str(e)}\nJSON: {json_str[:200]}...")
                                console_ui.display_response(content)
                                return False

                tool_name = tool_call.get("tool")
                tool_args = tool_call.get("args", {})
                
                # Get the tool from our map
                tool = self.tools_map.get(tool_name)
                
                if tool:
                    console_ui.display_tool_execution(tool_name)
                    
                    # Execute the tool
                    if isinstance(tool_args, dict):
                        result = await tool.execute(**tool_args)
                    else:
                        result = await tool.execute(tool_args)
                    
                    # Display the tool result
                    console_ui.display_tool_result(tool_name, str(result))
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "user",
                        "content": f"Tool Output ({tool_name}):\n{result}"
                    })
                    
                    # Return True to continue the loop and get AI's response to the tool output
                    return True
                else:
                    console_ui.display_error(f"Tool '{tool_name}' not found")
                    
            except json.JSONDecodeError as e:
                console_ui.display_error(f"Error parsing tool JSON: {e}\nContent: {json_str[:100]}...")
        
        # No tool call found, display the response with Markdown
        console_ui.display_response(content)
        return False
