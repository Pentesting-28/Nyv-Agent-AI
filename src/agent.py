import os
import json

class Agent:
    def __init__(self):
        self.set_tools()
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant who speaks Spanish and you are very concise with your answers."
            }
        ]

    def set_tools(self):
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_files_in_directory",
                    "description": "List files in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to list files from"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_files",
                    "description": "Read a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_or_update_files",
                    "description": "Create or Update a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path of the file to create or update"
                            },
                            "prev_text": {
                                "type": "string",
                                "description": "The text to be searched for and replaced (can be empty for new files)"
                            },
                            "new_text": {
                                "type": "string",
                                "description": "The text that will replace prev_text (or the text for a new file)"
                            }
                        },
                        "required": ["path", "new_text"]
                    }
                }
            },
        ]

    def list_files_in_directory(self, directory: str="."):
        print("⚙️ Tool called: list_files_in_directory")
        try:
            files = os.listdir(directory)
            return {"files": files}
        except Exception as e:
            return {"Error": f"Error listing directory: {str(e)}"}

    def read_files(self, path: str):
        print("⚙️ Tool called: read_files")
        try:
            with open(file=path, mode="r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return {"Error": f"Error reading file: {str(e)}"}

    def create_or_update_files(self, path: str, prev_text: str = "", new_text: str = ""):
        print("⚙️ Tool called: create_or_update_files")
        try:
            isset_file = os.path.exists(path)
            if isset_file and prev_text:
                # Read the file
                content_file = self.read_files(path)
                if prev_text not in content_file:
                    return f"Text {prev_text} not found in the file"
                
                # Replace the text
                content_file = content_file.replace(prev_text, new_text)
            else:
                # Create or sobreescribe the file
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                
                content_file = new_text

            with open(file=path, mode="w", encoding="utf-8") as f:
                f.write(content_file)

            type_action = "Update" if isset_file and prev_text else "Created"

            return f"File {path} {type_action} successfully!"
        except Exception as e:
            return {"Error": f"Error creating/updating file: {str(e)}"}
        
    def process_response(self, response):

        if not response.choices:
            return False
        
        response_message = response.choices[0].message
        content = response_message.content
        tool_calls = response_message.tool_calls
        refusal = getattr(response_message, 'refusal', None)

        if tool_calls:
            self.messages.append(response_message)
            
            available_functions = {
                "list_files_in_directory": self.list_files_in_directory,
                "read_files": self.read_files,
                "create_or_update_files": self.create_or_update_files
            }
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                
                if function_to_call:
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        function_response = function_to_call(**function_args)
                        
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": str(function_response),
                            }
                        )
                    except Exception as e:
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": f"Error executing tool: {str(e)}",
                            }
                        )
                else:
                    self.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error: Tool '{function_name}' not found.",
                        }
                    )
                
            return True
        elif refusal:
            print(f"🚫 REJECTED: {refusal}")

        elif content:
            print(f"Assistant: {content}")
            self.messages.append({"role": "assistant", "content": content})

        else:
            print("❓ Empty or unexpected response")
    
        return False