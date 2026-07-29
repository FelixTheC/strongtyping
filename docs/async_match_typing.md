## a_match_typing

`a_match_typing` is the runtime type-checking decorator for coroutine functions. Import it from
`strongtyping.astrong_typing` and apply it to an `async def` function. The decorated function remains awaitable.

```python
from strongtyping.astrong_typing import a_match_typing
import asyncio


@a_match_typing
async def fetch_user(user_id: int) -> dict[str, str]:
    return {"id": str(user_id)}


async def main() -> None:
    user = await fetch_user(42)
    await fetch_user("42")  # raises TypeMismatch before fetch_user runs


asyncio.run(main())
```

Type checks are run without blocking the event loop. As with `match_typing`, only parameters that have annotations
are checked.

### Large containers and runtime

`a_match_typing` performs type checks in a worker thread. This keeps the event loop responsive while validating large
containers, including nested dictionaries. The checks still have a runtime cost, so use the same type annotations and
cache settings you would use with `match_typing`; the async wrapper is intended to avoid blocking other coroutines,
not to make validation intrinsically faster.

### Configuration

Use `a_match_typing(...)` when configuration is needed. Its options mirror `match_typing`:

```python
from strongtyping.astrong_typing import a_match_typing


@a_match_typing(excep_raise=None, allow_duck_typing=True, cache_size=100)
async def handle(payload: dict[str, str]) -> None:
    ...
```

- `excep_raise`: exception to raise for invalid arguments; pass `None` to emit a `RuntimeWarning` instead.
- `allow_duck_typing`: accept compatible duck-typed values.
- `cache_size`: cache successful argument checks.
- `validate_return`: validate an annotated return value.
- `severity`: control checking through the same severity settings as `match_typing`.
- `subclass`: control subclass handling as with `match_typing`.

The function itself must be asynchronous and callers must `await` it. For regular functions, continue to use
[`match_typing`](match_typing.md).
