from _typeshed import Incomplete


class TypeMismatch(AttributeError):
    def __init__(
        self,
        message,
        failed_params: Incomplete | None = ...,
        param_values: Incomplete | None = ...,
        annotations: Incomplete | None = ...,
    ) -> None: ...


class ValidationError(Exception):
    def __init__(self, message) -> None: ...


class UndefinedKey(Exception):
    def __init__(self, message) -> None: ...
