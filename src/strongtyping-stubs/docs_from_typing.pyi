import inspect
from _typeshed import Incomplete
from strongtyping.strong_typing_utils import (
    get_origins as get_origins,
    get_possible_types as get_possible_types,
)
from typing import Any, Callable

Pattern: Incomplete

def getsource(object: Any) -> str: ...

ARGUMENT_TYPE: Incomplete

def union_types(val: Any, type_origins: Any) -> str: ...
def get_type_info(val: Any, type_origins: Any) -> str: ...
def docs_from_typing_numpy_format(
    annotations: dict[str, Any],
    additional_infos: dict[str, str],
    func_params: dict[str, inspect.Parameter],
    remove_linebreak: bool,
    func_info: str,
) -> tuple[str, str]: ...
def docs_from_typing_reST_format(
    annotations: dict[str, Any],
    additional_infos: dict[str, str],
    func_params: dict[str, inspect.Parameter],
    remove_linebreak: bool,
    func_info: str,
) -> tuple[str, str]: ...
def docs_from_typing(func: Callable[..., Any], remove_linebreak: bool, style: str) -> Any: ...
def rest_docs_from_typing(
    _func: Callable[..., Any] | None = None,
    *,
    insert_at: str | None = None,
    remove_linebreak: bool = False,
) -> Any: ...
def numpy_docs_from_typing(
    _func: Callable[..., Any] | None = None,
    *,
    insert_at: str | None = None,
    remove_linebreak: bool = False,
) -> Any: ...
def class_docs_from_typing(_cls: type[Any] | None = None, *, doc_type: str = "reST") -> Any: ...
