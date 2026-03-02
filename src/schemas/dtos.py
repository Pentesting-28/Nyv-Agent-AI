from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class MessageDTO:
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"role": self.role}
        if self.content is not None: d["content"] = self.content
        if self.tool_calls is not None: d["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None: d["tool_call_id"] = self.tool_call_id
        if self.name is not None: d["name"] = self.name
        return d

@dataclass
class ToolCallDTO:
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class ToolResultDTO:
    tool_call_id: str
    name: str
    content: str
