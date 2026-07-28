from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from _typeshed import Incomplete

from strongtyping.config import SEVERITY_LEVEL as SEVERITY_LEVEL

T = TypeVar("T")
P = ParamSpec("P")
logger: Incomplete
ORIGINAL_DUCK_TYPES: Any
CACHE_IGNORE_CLASS_FUNCTIONS: Incomplete

def get_safe_cache_key(args, kwargs): ...
def remove_subclass(args: Any, subclass: bool) -> Any: ...

SEVERITY_CONFIG: Incomplete
exclude_builtins: Incomplete

def install_st_m() -> None: ...
def action(f: Callable[..., Any], frefs: str, type_function: Any) -> Any: ...
