"""Types for Claude API."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from anthropic.types import Message

class ToolChoice(BaseModel):
    """Tool choice configuration"""
    type: Literal["tool"]
    name: str

class ChatRequest(BaseModel):
    """Complete chat request configuration"""
    model: str
    messages: List[dict[str, Any]]
    system: str = ""
    temperature: float = Field(ge=0, le=1, default=0)
    max_tokens: int = Field(ge=0, default=4096)
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[ToolChoice] = None
    stream: bool = False

    @field_validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("temperature must be between 0 and 1")
        return v

    @field_validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v < 0:
            raise ValueError("max_tokens must be positive")
        return v