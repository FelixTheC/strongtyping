from collections.abc import Callable as Callable
from strongtyping.cached_set import CachedSet as CachedSet
from strongtyping.config import SEVERITY_LEVEL as SEVERITY_LEVEL
from strongtyping.exceptions import TypeMismatch as TypeMismatch
from strongtyping.strong_typing_utils import (
    check_type as check_type,
    default_return_queue as default_return_queue,
    get_origins as get_origins,
)
from strongtyping.utils import (
    CACHE_IGNORE_CLASS_FUNCTIONS as CACHE_IGNORE_CLASS_FUNCTIONS,
    get_safe_cache_key as get_safe_cache_key,
    get_severity_level as get_severity_level,
    remove_subclass as remove_subclass,
)
from typing import Any

def a_match_typing(
    _func: Callable[..., Any] | None = None,
    *,
    excep_raise: type[Exception] = ...,
    subclass: bool = False,
    severity: str = "env",
    **kwargs: Any,
) -> Any: ...
