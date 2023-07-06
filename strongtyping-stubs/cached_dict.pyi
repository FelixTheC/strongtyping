from _typeshed import Incomplete
from typing import Any, Union

class CachedDict(dict):
    memory_limit: Incomplete
    def __init__(self, memory_limit: Union[int, float] = ..., *args, **kwargs) -> None: ...
    def __setitem__(self, key: Any, value: Any): ...
