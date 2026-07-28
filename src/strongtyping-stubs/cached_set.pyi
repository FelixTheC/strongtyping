from collections import deque
from typing import Any

from _typeshed import Incomplete

class CachedSet(set[Any]):
    order: deque[Any]
    max_size: Incomplete
    def __init__(self, memory_limit: float = 1, *args: Any, **kwargs: Any) -> None: ...
    def add(self, element: Any) -> None: ...
