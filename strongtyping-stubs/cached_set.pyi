from typing import Any, Union

class CachedSet(set):
    memory_limit: Any = ...
    def __init__(self, memory_limit: Union[int, float]=..., *args: Any, **kwargs: Any) -> None: ...
    def add(self, element: Any) -> None: ...