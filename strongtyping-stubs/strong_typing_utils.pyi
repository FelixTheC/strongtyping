import typing
from strongtyping._utils import install_st_m as install_st_m
from typing import Any, _GenericAlias

extension_module: bool

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
def checking_typing_set(arg: Any, possible_types: tuple, *args: Any) -> Any: ...
def checking_typing_type(arg: Any, possible_types: tuple, *args: Any) -> Any: ...
def checking_typing_union(arg: Any, possible_types: tuple, mro: Any) -> Any: ...
def checking_typing_iterator(arg: Any, *args: Any) -> Any: ...
def checking_typing_callable(arg: Any, possible_types: tuple, *args: Any) -> Any: ...
def checking_typing_tuple(arg: Any, possible_types: tuple, *args: Any) -> Any: ...
def checking_typing_list(arg: Any, possible_types: tuple, *args: Any) -> Any: ...
def checking_ellipsis(arg: Any, possible_types: Any): ...
def checking_typing_json(arg: Any, possible_types: Any, *args: Any): ...
def checking_typing_generator(arg: Any, possible_types: Any, *args: Any): ...
def checking_typing_literal(arg: Any, possible_types: Any, *args: Any): ...
def checking_typing__validator(arg: Any, possible_types: Any, *args: Any): ...
def checking_typing_validator(arg: Any, possible_types: Any, *args: Any): ...
def module_checking_typing_list(arg: Any, possible_types: Any) -> Any: ...
def module_checking_typing_dict(arg: Any, possible_types: Any) -> Any: ...
def module_checking_typing_set(arg: Any, possible_types: Any) -> Any: ...
def module_checking_typing_tuple(arg: Any, possible_types: Any) -> Any: ...

supported_typings: Any
m: Any
supported_modules: Any

def check_type(argument: Any, type_of: Any, mro: bool = ..., **kwargs: Any): ...

class _Validator(_GenericAlias):
    def __getitem__(self, item: Any) -> None: ...
    def __hash__(self) -> Any: ...

def Validator(self, parameters: Any, *args: Any, **kwargs: Any): ...

Validator: Any