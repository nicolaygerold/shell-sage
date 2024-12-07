from typing import Any, Dict, List, Literal, Optional, Union

from anthropic.types import Message, Usage
from pydantic import BaseModel, Field, validator


class ToolChoice(BaseModel):
    """Configuration for tool selection behavior"""
    type: Literal["tool", "any", "auto"]
    name: Optional[str] = None

    @classmethod
    def from_choice(cls, choose: Union[str, bool, None]) -> 'ToolChoice':
        """Create a tool choice configuration

        Args:
            choose: If str, force specific tool. If True, allow any. If None/False, auto.

        Returns:
            ToolChoice: Configured tool choice
        """
        if isinstance(choose, str):
            return cls(type="tool", name=choose)
        return cls(type="any" if choose else "auto")

    @validator('type')
    def validate_type(cls, v):
        allowed = {"tool", "any", "auto"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v

class ToolResult(BaseModel):
    """Result from a tool execution"""
    tool_use_id: str
    content: str
    type: Literal["tool_result"] = "tool_result"

class Usage(BaseModel):
    """Token usage tracking"""
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cache_creation_input_tokens: int = Field(ge=0, default=0)
    cache_read_input_tokens: int = Field(ge=0, default=0)

    @property
    def total(self) -> int:
        """Calculate total tokens used"""
        return (
            self.input_tokens +
            self.output_tokens +
            self.cache_creation_input_tokens +
            self.cache_read_input_tokens
        )

    def calculate_cost(self, pricing: tuple[float, float, float, float]) -> float:
        """Calculate cost based on token usage and pricing

        Args:
            pricing: Tuple of (input_cost, output_cost, cache_write_cost, cache_read_cost)
                    per million tokens

        Returns:
            float: Cost in USD
        """
        input_cost, output_cost, cache_write_cost, cache_read_cost = pricing
        return sum([
            self.input_tokens * input_cost,
            self.output_tokens * output_cost,
            self.cache_creation_input_tokens * cache_write_cost,
            self.cache_read_input_tokens * cache_read_cost
        ]) / 1e6

    def __add__(self, other: 'Usage') -> 'Usage':
        """Add usage statistics"""
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_creation_input_tokens=self.cache_creation_input_tokens + other.cache_creation_input_tokens,
            cache_read_input_tokens=self.cache_read_input_tokens + other.cache_read_input_tokens
        )

class ChatMessage(BaseModel):
    """Single message in a chat conversation"""
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[Dict[str, Any]]]

    @validator('content')
    def validate_content(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("content cannot be empty string")
        return v

class ChatRequest(BaseModel):
    """Complete chat request configuration"""
    model: str
    messages: List[ChatMessage]
    system: str = ""
    temperature: float = Field(ge=0, le=1, default=0)
    max_tokens: int = Field(ge=0, default=4096)
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[ToolChoice] = None
    stream: bool = False

    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("temperature must be between 0 and 1")
        return v

    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v < 0:
            raise ValueError("max_tokens must be positive")
        return v