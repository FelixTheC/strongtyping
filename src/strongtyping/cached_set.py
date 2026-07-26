import sys
from collections import deque
from typing import Any, Union


class CachedSet(set[Any]):
    """
    Warning only use for caching when Memory limit is reached all items will be cleared
    """

    order: deque[Any]

    def __init__(self, memory_limit: Union[int, float] = 1, *args: Any, **kwargs: Any) -> None:
        """
        :param memory_limit: in MB
        """
        super().__init__()
        self.max_size = memory_limit
        self.order = deque()

    def add(self, element: Any) -> None:
        if sys.getsizeof(self) > self.max_size:
            self.clear()
        super().add(element)
