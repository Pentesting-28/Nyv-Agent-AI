import pytest
from src.schemas.dtos import MessageDTO, ToolCallDTO, ToolResultDTO

def test_message_dto_to_dict():
    dto = MessageDTO(role="user", content="Hello")
    expected = {"role": "user", "content": "Hello"}
    assert dto.to_dict() == expected

def test_message_dto_with_tool_calls():
    tool_calls = [{"id": "1", "type": "function", "function": {"name": "test", "arguments": "{}"}}]
    dto = MessageDTO(role="assistant", content=None, tool_calls=tool_calls)
    d = dto.to_dict()
    assert d["role"] == "assistant"
    assert "content" not in d
    assert d["tool_calls"] == tool_calls

def test_tool_call_dto():
    dto = ToolCallDTO(id="123", name="test_tool", arguments={"input": "val"})
    assert dto.id == "123"
    assert dto.name == "test_tool"
    assert dto.arguments == {"input": "val"}

def test_tool_result_dto():
    dto = ToolResultDTO(tool_call_id="123", name="test_tool", content="Output")
    assert dto.tool_call_id == "123"
    assert dto.name == "test_tool"
    assert dto.content == "Output"
