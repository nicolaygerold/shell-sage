import logging
from typing import Any, Dict, Iterator, List, Optional, Union

from anthropic import Anthropic
from anthropic.types import Message

from .models import MODEL_TYPES, PRICING, TEXT_ONLY_MODELS
from .types import ChatMessage, ChatRequest, ToolChoice, ToolResult, Usage

logger = logging.getLogger(__name__)

class Client:
    """Production-ready Claude API client"""

    def __init__(self,
                 model: str,
                 api_key: Optional[str] = None,
                 log_usage: bool = False) -> None:
        """Initialize Claude client"""
        if model not in MODEL_TYPES:
            raise ValueError(f"Invalid model: {model}")

        self.model = model
        self.text_only = model in TEXT_ONLY_MODELS
        self.usage_log: List[Usage] = [] if log_usage else None

        try:
            self.client = Anthropic(
                api_key=api_key,
                default_headers={'anthropic-beta': 'prompt-caching-2024-07-31'}
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Claude client: {e}")

    def get_completion(self,
                      messages: List[Union[Dict[str, Any], ChatMessage]],
                      **kwargs) -> Union[Message, Iterator[str]]:
        """Get completion from Claude"""
        # Convert dict messages to ChatMessage if needed
        processed_messages = [
            m if isinstance(m, ChatMessage) else ChatMessage(**m)
            for m in messages
        ]

        # Create and validate request
        request = ChatRequest(
            model=self.model,
            messages=processed_messages,
            **kwargs
        )

        try:
            if request.stream:
                return self._stream_response(request.dict(exclude_none=True))
            return self._get_response(request.dict(exclude_none=True))
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            raise RuntimeError(f"Claude API call failed: {e}")

    def _get_response(self, request: Dict[str, Any]) -> Message:
        """Make synchronous API call"""
        response = self.client.messages.create(**request)
        if self.usage_log is not None:
            self.usage_log.append(Usage(**response.usage.dict()))
        return response

    def _stream_response(self, request: Dict[str, Any]) -> Iterator[str]:
        """Stream API response"""
        with self.client.messages.stream(**request) as stream:
            for chunk in stream.text_stream:
                yield chunk
            if self.usage_log is not None:
                self.usage_log.append(Usage(**stream.get_final_message().usage.dict()))