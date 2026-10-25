from typing import Any

class TypeMismatch(AttributeError):
    def __init__(
        self,
        message: str,
        failed_params: Any = None,
        param_values: Any = None,
        annotations: Any = None,
    ) -> None: ...

class ValidationError(Exception):
    def __init__(self, message: str) -> None: ...

class UndefinedKey(Exception):
    def __init__(self, message: str) -> None: ...
