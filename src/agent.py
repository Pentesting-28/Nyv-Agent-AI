import os
import json
from pprint import pprint
from models.agent_model import AgentModel
from tools import get_all_tools
class Agent(AgentModel):
    def __init__(self):
        self.tools = get_all_tools()
        self.messages = []
        # self.messages = [
        #     {
        #         "role": "system",
        #         "content": "You are a helpful assistant who speaks Spanish and you are very concise with your answers."
        #     }
        # ]

    async def build_system_prompt(self):
        return "You are a helpful assistant who speaks Spanish and you are very concise with your answers."
        
    async def process_response(self, response):

        if not response.get("choices"):
            return False
        
        response_message = response
        pprint(response_message)

        # content = response_message.get("content", "")
        # tool_calls = response_message.get("tool_calls", [])

        # if tool_calls:
        #     self.messages.append(response_message)
            
        #     available_functions = {}
            
        #     for tool_call in tool_calls:
        #         function_name = tool_call.function.name
        #         function_to_call = available_functions.get(function_name)
                
        #         if function_to_call:
        #             try:
        #                 function_args = json.loads(tool_call.function.arguments)
        #                 function_response = function_to_call(**function_args)
                        
        #                 self.messages.append(
        #                     {
        #                         "tool_call_id": tool_call.id,
        #                         "role": "tool",
        #                         "name": function_name,
        #                         "content": str(function_response),
        #                     }
        #                 )
        #             except Exception as e:
        #                 self.messages.append(
        #                     {
        #                         "tool_call_id": tool_call.id,
        #                         "role": "tool",
        #                         "name": function_name,
        #                         "content": f"Error executing tool: {str(e)}",
        #                     }
        #                 )
        #         else:
        #             self.messages.append(
        #                 {
        #                     "tool_call_id": tool_call.id,
        #                     "role": "tool",
        #                     "name": function_name,
        #                     "content": f"Error: Tool '{function_name}' not found.",
        #                 }
        #             )
                
        #     return True
        # elif content:
        #     print(f"Assistant: {content}")
        #     self.messages.append({"role": "assistant", "content": content})
        # else:
        #     print("❓ Empty or unexpected response")
    
        return False