from _typeshed import Incomplete
from typing import Any, Union

class CachedSet(set):
    memory_limit: Incomplete
    def __init__(self, memory_limit: Union[int, float] = ..., *args, **kwargs) -> None: ...
    def add(self, element: Any) -> None: ...
