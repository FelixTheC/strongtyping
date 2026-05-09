from _typeshed import Incomplete
from strongtyping.config import SEVERITY_LEVEL as SEVERITY_LEVEL
from typing import Any, Callable, Type, TypeVar, Union

logger: Incomplete
ORIGINAL_DUCK_TYPES: Incomplete
T = TypeVar('T')

def remove_subclass(args: Any, subclass: T) -> T: ...

SEVERITY_CONFIG: Incomplete

def _severity_level(severity_: Union[str, SEVERITY_LEVEL]) -> SEVERITY_LEVEL | int: ...

exclude_builtins: Incomplete

def _get_new(typing_func: Callable[[T], T], excep_raise: Type[Exception] = ..., cache_size: int = ..., severity: str = ..., **kwargs: Any) -> Callable[[Type[T]], Type[T]]: ...
def install_st_m() -> None: ...
def action(f: Any, frefs: Any, type_function: Any) -> Any: ...
