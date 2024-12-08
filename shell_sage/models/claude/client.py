"""Client for Claude API."""

import logging
import os
from typing import Any, Dict, Iterator, List, Optional, Union

from anthropic import Anthropic
from anthropic.types import Usage, Message

from .types import ChatRequest
from .models import MODEL_TYPES, TEXT_ONLY_MODELS
from .utils import mk_msg
from shell_sage.config import load_api_key

logger = logging.getLogger(__name__)

class Client:
    """Production-ready Claude API client"""

    def __init__(self,
                 model: str,
                 api_key: Optional[str] = None,
                 log_usage: bool = False) -> None:
        """Initialize Claude client

        You should set your API key in your ~/.zshrc or ~/.bashrc file:

        export ANTHROPIC_API_KEY="sk-ant-api03-..."

        Args:
            model: The Claude model to use
            api_key: Optional API key. If not provided, will check ANTHROPIC_API_KEY env var
            log_usage: Whether to log API usage statistics

        Raises:
            ValueError: If model is invalid or API key is not available
            ConnectionError: If client initialization fails
        """
        if model not in MODEL_TYPES:
            raise ValueError(f"Invalid model: {model}")

        # API key validation with multiple fallbacks
        self.api_key = (
            api_key or
            os.environ.get('ANTHROPIC_API_KEY') or
            load_api_key()
        )

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. Please either:\n"
                "1. Run 'shell-sage setup' to configure your API key\n"
                "2. Set the ANTHROPIC_API_KEY environment variable\n"
                "3. Pass the API key directly\n"
                "\nGet your API key from: https://console.anthropic.com/account/keys"
            )

        self.model = model
        self.text_only = model in TEXT_ONLY_MODELS
        self.usage_log: List[Usage] = [] if log_usage else None

        try:
            self.client = Anthropic(
                api_key=self.api_key,
                default_headers={'anthropic-beta': 'prompt-caching-2024-07-31'}
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Claude client: {e}")

    def get_completion(self,
                      messages: list[dict[str, Any] | Message],
                      **kwargs) -> Message | Iterator[str]:
        """Get completion from Claude

        Args:
            messages: List of messages in either dict or Message format
            **kwargs: Additional parameters for the request

        Returns:
            Message or Iterator[str] if streaming

        Raises:
            RuntimeError: If API call fails
            ValueError: If message format is invalid
        """
        try:
            # Create and validate request
            request = ChatRequest(
                model=self.model,
                messages=messages,
                **kwargs
            )

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
            self.usage_log.append(Usage(**response.usage.model_dump()))
        return response

    def _stream_response(self, request: Dict[str, Any]) -> Iterator[str]:
        """Stream API response"""
        with self.client.messages.stream(**request) as stream:
            for chunk in stream.text_stream:
                yield chunk
            if self.usage_log is not None:
                self.usage_log.append(Usage(**stream.get_final_message().usage.model_dump()))