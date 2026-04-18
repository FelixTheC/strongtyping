import re
from functools import wraps
from typing import Callable, Optional, Protocol, TypedDict, TypeGuard

from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import TypeMismatch, ValidationError


def validate_typed_dict(base: TypedDict, /, data: dict) -> bool:
    # noinspection PyTypeHints
    @match_typing
    def inner(obj: base):
        pass

    try:
        inner(data)
    except (TypeMismatch, ValidationError):
        return False
    return True


def Gt(limit: int, /) -> Callable[[int], bool]:
    def gt(val: int) -> bool:
        return val > limit
    return gt


def Len(*, lower: int, upper: Optional[int] = None) -> Callable[[str | dict | list | tuple | set], bool]:
    def len_validator(val: str | dict | list | tuple | set) -> bool:
        res = len(val) >= lower
        if upper is not None:
            res = res and len(val) <= upper
        return res
    return len_validator


def Regex(regex: str, /) -> Callable[[str], bool]:
    def regex_validator(val: str) -> bool:
        return bool(re.match(regex, val))
    return regex_validator
