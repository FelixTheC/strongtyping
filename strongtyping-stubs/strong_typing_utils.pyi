import typing
from typing import Any, Optional

from strongtyping._utils import install_st_m as install_st_m

extension_module: bool
empty: Any
default_return_queue: Any

class TypeMisMatch(AttributeError):
    def __init__(self, message: Any) -> None: ...

class ValidationError(Exception):
    def __init__(self, message: Any) -> None: ...

py_version: Any
typing_base_class: Any
typing_base_class = typing.GenericMeta

def get_possible_types(typ_to_check: Any) -> typing.Union[tuple, None]: ...
def get_origins(typ_to_check: Any) -> tuple: ...
def checking_typing_dict(arg: Any, possible_types: tuple, *args: Any) -> Any: ...
def checking_typing_set(arg: Any, possible_types: tuple, *args: Any, **kwargs: Any) -> Any: ...
def checking_typing_type(arg: Any, possible_types: tuple, *args: Any, **kwargs: Any) -> Any: ...
def checking_typing_union(arg: Any, possible_types: tuple, mro: Any, **kwargs: Any) -> Any: ...
def checking_typing_iterator(arg: Any, *args: Any, **kwargs: Any) -> Any: ...
def checking_typing_callable(arg: Any, possible_types: tuple, *args: Any, **kwargs: Any) -> Any: ...
def checking_typing_tuple(arg: Any, possible_types: tuple, *args: Any, **kwargs: Any) -> Any: ...
def checking_typing_list(arg: Any, possible_types: tuple, *args: Any, **kwargs: Any) -> Any: ...
def checking_ellipsis(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing_json(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing_generator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing_literal(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing__validator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing_validator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing__itervalidator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing_itervalidator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def checking_typing_iterable(arg: Any, possible_types: tuple, *args: Any, **kwargs: Any) -> Any: ...
def checking_typing_typedict_values(args: dict, required_types: dict, total: bool) -> Any: ...
def module_checking_typing_list(arg: Any, possible_types: Any) -> Any: ...
def module_checking_typing_dict(arg: Any, possible_types: Any) -> Any: ...
def module_checking_typing_set(arg: Any, possible_types: Any) -> Any: ...
def module_checking_typing_tuple(arg: Any, possible_types: Any) -> Any: ...
def module_checking_typing_validator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any): ...
def validate_object(value: Any, validation_func: Optional[Any] = ...): ...

supported_typings: Any
m: Any
supported_modules: Any

def check_type(argument: Any, type_of: Any, mro: bool = ..., **kwargs: Any): ...
