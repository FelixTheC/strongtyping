import typing
from typing import Any, Callable, Optional, Type

from strongtyping._utils import action as action, remove_subclass as remove_subclass
from strongtyping.cached_set import CachedSet as CachedSet
from strongtyping.strong_typing_utils import (
    TypeMisMatch as TypeMisMatch,
    check_type as check_type,
    checking_typing_typedict_values as checking_typing_typedict_values,
    default_return_queue as default_return_queue,
    get_origins as get_origins,
    py_version as py_version,
)

def match_typing(
    _func: Any = ...,
    *,
    excep_raise: Type[Exception] = ...,
    subclass: bool = ...,
    severity: Any = ...,
    **kwargs: Any,
) -> Any: ...

class match_class_typing:
    def __new__(cls, instance: Optional[Any] = ..., *args: Any, **kwargs: Any): ...
    excep_raise: Any = ...
    cache_size: Any = ...
    severity: Any = ...
    cls: Any = ...
    def __init__(self, cls: Optional[Any] = ..., *args: Any, **kwargs: Any) -> None: ...
    def __getattr__(self, item: Any): ...
    @staticmethod
    def __has_annotations__(obj: Any): ...
    @property
    def is_typed_dict(self): ...
    def create_error_msg(self, args: dict) -> Any: ...
    def __call__(self, *args: Any, **kwargs: Any): ...

def getter(func: Any): ...
def setter(func: Any): ...
def getter_setter(func: Any): ...
