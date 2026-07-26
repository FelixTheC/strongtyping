from _typeshed import Incomplete
from strongtyping.config import SEVERITY_LEVEL as SEVERITY_LEVEL
from typing import Any, Callable, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")
logger: Incomplete
ORIGINAL_DUCK_TYPES: Any

def remove_subclass(args: Any, subclass: bool) -> Any: ...

SEVERITY_CONFIG: Incomplete

def get_severity_level(severity_: str | SEVERITY_LEVEL) -> int: ...

exclude_builtins: Incomplete

def install_st_m() -> None: ...
def action(f: Callable[..., Any], frefs: str, type_function: Any) -> Any: ...
