import abc
from functools import partial

from anthropic.types import TextBlock


def noop(x): return x

def not_(f):
    "Create a function that negates `f`"
    return lambda *args, **kwargs: not f(*args, **kwargs)

def filter_ex(iterable, f=noop, negate=False, gen=False, **kwargs):
    "Like `filter`, but passing `kwargs` to `f`, defaulting `f` to `noop`, and adding `negate` and `gen`"
    if f is None: f = lambda _: True
    if kwargs: f = partial(f,**kwargs)
    if negate: f = not_(f)
    res = filter(f, iterable)
    if gen: return res
    return list(res)

def first(x, f=None, negate=False, **kwargs):
    "First element of `x`, optionally filtered by `f`, or None if missing"
    x = iter(x)
    if f: x = filter_ex(x, f=f, negate=negate, gen=True, **kwargs)
    return next(x, None)

def find_block(r:abc.Mapping, # The message to look in
               blk_type:type=TextBlock  # The type of block to find
              ):
    "Find the first block of type `blk_type` in `r.content`."
    return first(o for o in r.content if isinstance(o,blk_type))

def contents(r):
    "Helper to get the contents from Claude response `r`."
    blk = find_block(r)
    if not blk and r.content: blk = r.content[0]
    return blk.text.strip() if hasattr(blk,'text') else str(blk)