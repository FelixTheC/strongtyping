from _typeshed import Incomplete
from collections import deque
from typing import Any

class CachedDict(dict[Any, Any]):
    order: deque[Any]
    max_size: Incomplete
    def __init__(self, memory_limit: int | float = 1, *args: Any, **kwargs: Any) -> None: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
