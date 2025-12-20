"""
File System Tools
Provides granular tools for file system operations: list, read, write, mkdir, delete.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union, List
from src.models.function_model import BaseTool, tool_registry

class FileSystemBaseTool(BaseTool):
    """Base class for file system tools with common path validation."""
    
    def _validate_path(self, path: str) -> Path:
        """
        Validate and resolve path.
        Ensures path is safe to access (within user's home directory).
        """
        # Get current working directory and user home
        cwd = Path(os.getcwd()).resolve()
        user_home = Path.home().resolve()
        
        # Handle absolute vs relative paths
        target_path = Path(path)
        if not target_path.is_absolute():
            target_path = (cwd / target_path).resolve()
        else:
            target_path = target_path.resolve()
            
        # Security check: Ensure target is within User Home
        # We allow access to Documents, Music, Desktop, etc.
        if not str(target_path).startswith(str(user_home)):
            raise ValueError(f"Access denied: Path '{path}' is outside the user's home directory ({user_home}).")
            
        return target_path

class ListDirectoryTool(FileSystemBaseTool):
    def __init__(self):
        super().__init__(
            name="list_directory",
            description="List files and directories in a given path. Returns names and types (file/dir).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (default: current directory)",
                        "default": "."
                    }
                },
                "required": []
            }
        )

    async def execute(self, path: str = ".") -> str:
        try:
            target_path = self._validate_path(path)
            
            if not target_path.exists():
                return f"Error: Path '{path}' does not exist."
            
            if not target_path.is_dir():
                return f"Error: Path '{path}' is not a directory."
            
            items = []
            for item in target_path.iterdir():
                type_str = "DIR " if item.is_dir() else "FILE"
                items.append(f"[{type_str}] {item.name}")
            
            if not items:
                return f"Directory '{path}' is empty."
                
            return f"Contents of '{path}':\n" + "\n".join(sorted(items))
            
        except Exception as e:
            return f"Error listing directory: {str(e)}"

class ReadFileTool(FileSystemBaseTool):
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the content of a file. Returns the text content.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        )

    async def execute(self, path: str) -> str:
        try:
            target_path = self._validate_path(path)
            
            if not target_path.exists():
                return f"Error: File '{path}' does not exist."
            
            if not target_path.is_file():
                return f"Error: Path '{path}' is not a file."
            
            try:
                content = target_path.read_text(encoding='utf-8')
                return f"Content of '{path}':\n\n{content}"
            except UnicodeDecodeError:
                return f"Error: File '{path}' appears to be binary and cannot be read as text."
                
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WriteFileTool(FileSystemBaseTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        )

    async def execute(self, path: str, content: str) -> str:
        try:
            target_path = self._validate_path(path)
            
            # Create parent directories if they don't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            target_path.write_text(content, encoding='utf-8')
            return f"Successfully wrote to '{path}'."
                
        except Exception as e:
            return f"Error writing file: {str(e)}"

class MakeDirectoryTool(FileSystemBaseTool):
    def __init__(self):
        super().__init__(
            name="make_directory",
            description="Create a new directory. Creates parent directories if needed.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the directory to create"
                    }
                },
                "required": ["path"]
            }
        )

    async def execute(self, path: str) -> str:
        try:
            target_path = self._validate_path(path)
            
            if target_path.exists():
                return f"Error: Path '{path}' already exists."
            
            target_path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory '{path}'."
                
        except Exception as e:
            return f"Error creating directory: {str(e)}"

class DeleteTool(FileSystemBaseTool):
    def __init__(self):
        super().__init__(
            name="delete_item",
            description="Delete a file or directory. Be careful with this tool.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory to delete"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Set to true to delete non-empty directories",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        )

    async def execute(self, path: str, recursive: bool = False) -> str:
        try:
            target_path = self._validate_path(path)
            
            if not target_path.exists():
                return f"Error: Path '{path}' does not exist."
            
            if target_path.is_file():
                target_path.unlink()
                return f"Successfully deleted file '{path}'."
            elif target_path.is_dir():
                if recursive:
                    shutil.rmtree(target_path)
                    return f"Successfully deleted directory '{path}' and all contents."
                else:
                    try:
                        target_path.rmdir()
                        return f"Successfully deleted empty directory '{path}'."
                    except OSError:
                        return f"Error: Directory '{path}' is not empty. Use recursive=true to delete it."
            
            return f"Error: Unknown item type for '{path}'."
                
        except Exception as e:
            return f"Error deleting item: {str(e)}"

# Instantiate and register tools
list_directory_tool = ListDirectoryTool()
tool_registry.register(list_directory_tool)

read_file_tool = ReadFileTool()
tool_registry.register(read_file_tool)

write_file_tool = WriteFileTool()
tool_registry.register(write_file_tool)

make_directory_tool = MakeDirectoryTool()
tool_registry.register(make_directory_tool)

delete_tool = DeleteTool()
tool_registry.register(delete_tool)
