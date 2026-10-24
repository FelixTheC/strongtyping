from _typeshed import Incomplete
from collections.abc import Callable as Callable, Mapping, Sequence
from strongtyping.config import SeverityLevel as SeverityLevel
from typing import Any, ParamSpec, TypeVar

T = TypeVar('T')
P = ParamSpec('P')
logger: Incomplete
ORIGINAL_DUCK_TYPES: Any
CACHE_IGNORE_CLASS_FUNCTIONS: Incomplete

def get_safe_cache_key(args: Sequence[Any], kwargs: Mapping[Any, Any]) -> tuple[tuple[int | str, ...], tuple[int | str, ...]]: ...
def remove_subclass(args: Any, subclass: bool) -> Any: ...

SEVERITY_CONFIG: Incomplete

def get_severity_level(severity_: str | SeverityLevel) -> int: ...

exclude_builtins: Incomplete

def install_st_m() -> None: ...
def action(f: Callable[..., Any], frefs: str, type_function: Any) -> Any: ...
