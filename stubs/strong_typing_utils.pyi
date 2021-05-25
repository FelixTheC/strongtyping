from typing import Any, Union, Callable


class TypeMisMatch(AttributeError):
    def __init__(self, message: str) -> None: ...

class ValidationError(Exception):
    def __init__(self, message: str) -> None: ...

class _Validator:
    def __getitem__(self, item: str) -> None: ...

Validator: Union[Any, Callable]
