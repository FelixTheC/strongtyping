import re
from typing import Any, Callable, Optional, Sized, Type, TypeVar

from strongtyping.exceptions import TypeMismatch, ValidationError
from strongtyping.strong_typing import match_typing

T = TypeVar("T")


def validate_typed_dict(base: Type[Any], /, data: dict[Any, Any]) -> bool:
    # noinspection PyTypeHints
    @match_typing
    def inner(obj: Any) -> None:
        None

    try:
        if callable(base):
            inner(base(**data))
        inner(data)
    except (TypeMismatch, ValidationError):
        return False
    return True


def Gt(limit: int, /) -> Callable[[int], bool]:
    """
    Validates if a value is greater than a specified limit.

    Args:
        limit (int): The lower bound of the range (exclusive).

    Returns:
        bool: True if it's greater than the limit, False otherwise.
    """

    def gt(val: int) -> bool:
        return val > limit

    return gt


def Gte(limit: int, /) -> Callable[[int], bool]:
    """
    Validates if a value is greater than or equal to a specified limit.

    Args:
        limit (int): The lower bound of the range (inclusive).

    Returns:
        bool: True if it's greater than or equal to the limit, False otherwise.
    """

    def gte(val: int) -> bool:
        return val >= limit

    return gte


def Lt(limit: int, /) -> Callable[[int], bool]:
    """
    Validates if a value is less than a specified limit.

    Args:
        limit (int): The upper bound of the range (exclusive).

    Returns:
        bool: True if it's less than the limit, False otherwise.
    """

    def lt(val: int) -> bool:
        return val < limit

    return lt


def Lte(limit: int, /) -> Callable[[int], bool]:
    """
    Validates if a value is less than or equal to a specified limit.

    Args:
        limit (int): The upper bound of the range (inclusive).

    Returns:
        bool: True if it's less than or equal to the limit, False otherwise.
    """

    def lte(val: int) -> bool:
        return val <= limit

    return lte


def Range(lower: int, upper: int, /) -> Callable[[int], bool]:
    """
    Validates if a value is within a specified range.

    Args:
        lower (int): The lower bound of the range (inclusive).
        upper (int): The upper bound of the range (inclusive).

    Returns:
        bool: True if it's within the range, False otherwise.
    """

    def range_validator(val: int) -> bool:
        return lower <= val <= upper

    return range_validator


def IsPositive() -> Callable[[int], bool]:
    """
    Validates if a value is positive.

    Returns:
        bool: True if the value is positive, False otherwise.
    """

    def is_positive(val: int) -> bool:
        return val > 0

    return is_positive


def IsNegative() -> Callable[[int], bool]:
    """
    Validates if a value is negative.

    Returns:
        bool: True if the value is negative, False otherwise.
    """

    def is_negative(val: int) -> bool:
        return val < 0

    return is_negative


def IsUUid() -> Callable[[str], bool]:
    def is_uuid(val: str) -> bool:
        import uuid

        try:
            uuid.UUID(val)
        except ValueError:
            return False
        return True

    return is_uuid


def Len(*, lower: int, upper: Optional[int] = None) -> Callable[[Sized], bool]:
    """
    Validates if a value's length is within a specified range.

    Args:
        lower (int): The minimum length (inclusive).
        upper (Optional[int]): The maximum length (inclusive). If None, no upper limit is applied.

    Returns:
        bool: True if the length is within the range, False otherwise.
    """

    def len_validator(val: Sized) -> bool:
        res = len(val) >= lower
        if upper is not None:
            res = res and len(val) <= upper
        return res

    return len_validator


def Regex(regex: str, /) -> Callable[[str], bool]:
    """
    Validates if a value matches a specified regular expression.

    Args:
        regex (str): The regular expression pattern to match against.

    Returns:
        bool: True if the value matches the pattern, False otherwise.
    """

    def regex_validator(val: str) -> bool:
        return bool(re.match(regex, val))

    return regex_validator
