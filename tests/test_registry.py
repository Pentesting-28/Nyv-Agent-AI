import pytest
from src.core.registry import ToolRegistry
from tests.conftest import DummyTool

def test_registry_register_and_get():
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register_tool(tool)
    
    assert registry.get_tool("dummy_tool") == tool
    assert len(registry.get_all_tools()) == 1
    assert registry.get_all_tools()[0] == tool

def test_registry_get_nonexistent():
    registry = ToolRegistry()
    assert registry.get_tool("nonexistent") is None

def test_registry_get_definitions():
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register_tool(tool)
    
    definitions = registry.get_tools_definitions()
    assert len(definitions) == 1
    assert definitions[0]["type"] == "function"
    assert definitions[0]["function"]["name"] == "dummy_tool"
    assert "input" in definitions[0]["function"]["parameters"]["properties"]
