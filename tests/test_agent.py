import pytest
import json
from src.agent import Agent
from src.schemas.dtos import MessageDTO

@pytest.mark.asyncio
async def test_agent_direct_response(mock_llm_client, tool_registry):
    agent = Agent(mock_llm_client, tool_registry)
    mock_llm_client.add_response("Hello there!")
    
    result = await agent.run_cycle()
    
    assert result is False  # No tool called
    assert len(agent.messages) == 2  # System + Assistant
    assert agent.messages[-1]["content"] == "Hello there!"

@pytest.mark.asyncio
async def test_agent_json_tool_call(mock_llm_client, tool_registry):
    agent = Agent(mock_llm_client, tool_registry)
    
    # Simulate a JSON tool call in markdown
    tool_call_json = {
        "tool": "dummy_tool",
        "args": {"input": "test_value"}
    }
    content = f"I'll use the tool:\n```json\n{json.dumps(tool_call_json)}\n```"
    mock_llm_client.add_response(content)
    
    # We call run_cycle. It should return True because a tool was called.
    result = await agent.run_cycle()
    
    assert result is True
    assert len(agent.messages) == 3  # System + Assistant + Tool Output (user role)
    assert "Processed: test_value" in agent.messages[-1]["content"]

@pytest.mark.asyncio
async def test_agent_k2_tool_call(mock_llm_client, tool_registry):
    agent = Agent(mock_llm_client, tool_registry)
    
    # Simulate K2-Think format: <|tool_call_start|>[tool_name(arg1=val1)]<|tool_call_end|>
    content = "<|tool_call_start|>[dummy_tool(input=\"k2_value\")]<|tool_call_end|>"
    mock_llm_client.add_response(content)
    
    result = await agent.run_cycle()
    
    assert result is True
    assert "Processed: k2_value" in agent.messages[-1]["content"]

@pytest.mark.asyncio
async def test_agent_parameter_mapping(mock_llm_client, tool_registry):
    # This test verifies that 'file_path' is mapped to 'path' if 'path' is expected.
    # We'll use a mock tool that expects 'path'.
    from src.core.base import BaseTool
    class PathTool(BaseTool):
        def __init__(self):
            super().__init__("path_tool", "expects path", {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]})
        async def execute(self, path: str) -> str:
            return f"Path is {path}"
            
    tool_registry.register_tool(PathTool())
    agent = Agent(mock_llm_client, tool_registry)
    
    # LLM sends 'file_path' instead of 'path'
    tool_call = {"tool": "path_tool", "args": {"file_path": "mapped/path.txt"}}
    mock_llm_client.add_response(f"```json\n{json.dumps(tool_call)}\n```")
    
    result = await agent.run_cycle()
    
    assert result is True
    assert "Path is mapped/path.txt" in agent.messages[-1]["content"]
