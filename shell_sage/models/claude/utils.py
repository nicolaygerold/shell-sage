"""Utility functions for Claude API."""

import abc
from functools import partial
from typing import Any, Callable, Iterable, Optional, TypeVar

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

def find_block(r: abc.Mapping,
              blk_type: type = TextBlock) -> Optional[TextBlock]:
    """Find first content block of specified type in message.

    Args:
        r: Message containing content blocks
        blk_type: Type of block to find

    Returns:
        First matching block or None if not found
    """
    return first(o for o in r.content if isinstance(o, blk_type))

def contents(r: abc.Mapping) -> str:
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