"""Utility functiabc for Claude API."""

from collections.abc import Mapping

from functools import partial
from typing import Any, Callable, Iterable, Optional, TypeVar
import base64
from pathlib import Path

from anthropic.types import TextBlock

T = TypeVar('T')

def noop(x: Any) -> Any:
    """Identity function that returns its input unchanged."""
    return x

def not_(f: Callable) -> Callable:
    """Create a function that negates the result of the input function.

    Args:
        f: Function to negate

    Returns:
        A new function that returns the logical NOT of f's result
    """
    return lambda *args, **kwargs: not f(*args, **kwargs)

def filter_ex(iterable: Iterable[T],
             f: Optional[Callable] = noop,
             negate: bool = False,
             gen: bool = False,
             **kwargs) -> Iterable[T]:
    """Enhanced filter function with additional options.

    Args:
        iterable: Input sequence to filter
        f: Filter function (defaults to identity)
        negate: If True, invert the filter condition
        gen: If True, return generator instead of list
        **kwargs: Additional arguments passed to filter function

    Returns:
        Filtered sequence as list or generator
    """
    if f is None:
        f = lambda _: True
    if kwargs:
        f = partial(f, **kwargs)
    if negate:
        f = not_(f)
    res = filter(f, iterable)
    return res if gen else list(res)

def first(x: Iterable[T],
         f: Optional[Callable] = None,
         negate: bool = False,
         **kwargs) -> Optional[T]:
    """Get first element of sequence, optionally filtered.

    Args:
        x: Input sequence
        f: Optional filter function
        negate: If True, invert the filter condition
        **kwargs: Additional arguments passed to filter function

    Returns:
        First matching element or None if no match found
    """
    x = iter(x)
    if f:
        x = filter_ex(x, f=f, negate=negate, gen=True, **kwargs)
    return next(x, None)

def find_block(r: Mapping,
              blk_type: type = TextBlock) -> Optional[TextBlock]:
    """Find first content block of specified type in message.

    Args:
        r: Message containing content blocks
        blk_type: Type of block to find

    Returns:
        First matching block or None if not found
    """
    return first(o for o in r.content if isinstance(o, blk_type))

def contents(r: Mapping) -> str:
    """Extract text content from Claude API response.

    Args:
        r: Claude API response message

    Returns:
        Extracted text content as string
    """
    blk = find_block(r)
    if not blk and r.content:
        blk = r.content[0]
    return blk.text.strip() if hasattr(blk, 'text') else str(blk)

def mk_msg(content: str | bytes | list[str | bytes | Path] | dict[str, Any],
           role: str = "user") -> dict[str, Any]:
    """Create a standardized message format for Claude API.

    Args:
        content: Message content - can be string, bytes (image), list of contents, or pre-formatted dict
        role: Message role (defaults to "user")

    Returns:
        Dict containing formatted message

    Raises:
        ValueError: If content format is invalid
        TypeError: If content type is not supported
    """
    # If already formatted, return as-is
    if isinstance(content, dict) and "role" in content:
        return content

    # Handle list of contents
    if isinstance(content, list):
        formatted_contents = []
        for item in content:
            if isinstance(item, str):
                formatted_contents.append({"type": "text", "text": item})
            elif isinstance(item, bytes) or isinstance(item, Path):
                # Handle image data
                if isinstance(item, Path):
                    img_data = item.read_bytes()
                else:
                    img_data = item

                formatted_contents.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",  # Simplified - could detect mime type
                        "data": base64.b64encode(img_data).decode()
                    }
                })
            else:
                raise TypeError(f"Unsupported content type in list: {type(item)}")
        return {"role": role, "content": formatted_contents}

    # Handle single string
    if isinstance(content, str):
        return {
            "role": role,
            "content": [{"type": "text", "text": content}]
        }

    # Handle single image
    if isinstance(content, bytes) or isinstance(content, Path):
        if isinstance(content, Path):
            img_data = content.read_bytes()
        else:
            img_data = content

        return {
            "role": role,
            "content": [{
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64.b64encode(img_data).decode()
                }
            }]
        }

    raise TypeError(f"Unsupported content type: {type(content)}")

def mk_msgs(messages: list[str | bytes | list[str | bytes | Path] | dict[str, Any]],
            prefill: str = "") -> list[dict[str, Any]]:
    """Create a list of standardized messages for Claude API.

    Args:
        messages: List of messages to format
        prefill: Optional text to prefill the last assistant message

    Returns:
        List of formatted messages

    Raises:
        ValueError: If messages is empty
    """
    if not messages:
        raise ValueError("Messages list cannot be empty")

    formatted_msgs = []

    # Format all messages except the last one
    for msg in messages[:-1]:
        formatted_msgs.append(mk_msg(msg, "user"))
        formatted_msgs.append({"role": "assistant", "content": [{"type": "text", "text": ""}]})

    # Format the last message
    formatted_msgs.append(mk_msg(messages[-1], "user"))

    # Add prefill if provided
    if prefill:
        formatted_msgs.append({
            "role": "assistant",
            "content": [{"type": "text", "text": prefill}]
        })

    return formatted_msgs