from collections import deque
from typing import Any


class CachedDict(dict[Any, Any]):
    """
    Warning only use for caching when Memory limit is reached all items will be cleared
    """

    order: deque[Any]

    def __init__(self: "CachedDict", memory_limit: float = 1, *args: Any, **kwargs: Any) -> None:
        """
        :param memory_limit: in MB
        """
        super().__init__()
        self.max_size = memory_limit
        self.order = deque()

    def __setitem__(self: "CachedDict", key: Any, value: Any) -> None:
        if key not in self:
            if len(self) >= self.max_size:
                oldest = self.order.popleft()
                del self[oldest]
            self.order.append(key)
        super().__setitem__(key, value)
