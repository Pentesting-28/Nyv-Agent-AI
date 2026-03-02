import os
import sys
import io
import asyncio
from dotenv import load_dotenv

from . import console_ui
from src.core.registry import ToolRegistry
from src.llm.client_ai import ClientAI
from src.agent import Agent
from src.schemas.dtos import MessageDTO
from src.tools import (
    WebSearchTool, WebNavigateTool, ListDirectoryTool,
    ReadFileTool, WriteFileTool, MakeDirectoryTool,
    DeleteTool, MoveTool, CopyTool, GetFileInfoTool,
    SearchFilesTool, AppendFileTool, BatchMoveTool
)

def setup_encoding():
    # Force UTF-8 encoding for Windows console
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

async def main():
    setup_encoding()
    load_dotenv()

    # Initialize Registry and Tools
    registry = ToolRegistry()
    registry.register_tool(WebSearchTool(region="es-es"))
    registry.register_tool(WebNavigateTool())
    registry.register_tool(ListDirectoryTool())
    registry.register_tool(ReadFileTool())
    registry.register_tool(WriteFileTool())
    registry.register_tool(MakeDirectoryTool())
    registry.register_tool(DeleteTool())
    registry.register_tool(MoveTool())
    registry.register_tool(CopyTool())
    registry.register_tool(GetFileInfoTool())
    registry.register_tool(SearchFilesTool())
    registry.register_tool(AppendFileTool())
    registry.register_tool(BatchMoveTool())

    # Initialize LLM Client
    client_ai = ClientAI(
        api_key=os.getenv("UNIFIE_API_KEY"),
        base_url=os.getenv("UNIFIE_API_URL"),
        timeout=120.0
    )

    # Initialize Agent
    agent = Agent(llm_client=client_ai, tool_registry=registry)

    # Show welcome banner
    console_ui.display_welcome()
    
    # Chat loop
    while True:
        user_input = console_ui.prompt_user()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
            console_ui.display_goodbye()
            break
        
        # Display user message
        console_ui.display_user_message(user_input)
        
        # Add message to agent as DTO
        agent.add_message(MessageDTO(role="user", content=user_input))
        
        while True:
            # Show thinking spinner while waiting for response
            with console_ui.ThinkingSpinner():
                # Core execution cycle
                has_more_steps = await agent.run_cycle()
            
            if not has_more_steps:
                break

if __name__ == "__main__":
    asyncio.run(main())
