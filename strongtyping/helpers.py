import re
from typing import Any, Callable, Optional, Sized, Type, TypeVar

from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import TypeMismatch, ValidationError

T = TypeVar("T")


def validate_typed_dict(base: Type[Any], /, data: dict[Any, Any]) -> bool:
    # noinspection PyTypeHints
    @match_typing
    def inner(obj: Any) -> None:
        pass

    inner.__annotations__["obj"] = base

    try:
        inner(data)
    except (TypeMismatch, ValidationError):
        return False
    return True


def Gt(limit: int, /) -> Callable[[int], bool]:
    def gt(val: int) -> bool:
        return val > limit

    return gt


def Len(*, lower: int, upper: Optional[int] = None) -> Callable[[Sized], bool]:
    def len_validator(val: Sized) -> bool:
        res = len(val) >= lower
        if upper is not None:
            res = res and len(val) <= upper
        return res

    return len_validator


def Regex(regex: str, /) -> Callable[[str], bool]:
    def regex_validator(val: str) -> bool:
        return bool(re.match(regex, val))

    return regex_validator
