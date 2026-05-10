from typing import Annotated, TypedDict

import pytest
from strongtyping.exceptions import TypeMismatch, ValidationError
from strongtyping.helpers import (
    Gt,
    Gte,
    IsNegative,
    IsPositive,
    IsUUid,
    Len,
    Lt,
    Lte,
    Range,
    Regex,
    validate_typed_dict,
)
from strongtyping.strong_typing import match_class_typing, match_typing


def test_validate_typed_dict():
    @match_class_typing
    class MyDict(TypedDict):
        a: int
        b: str

    assert validate_typed_dict(MyDict, {"a": 1, "b": "s"}) is True
    assert validate_typed_dict(MyDict, {"a": "s", "b": "s"}) is False
    assert validate_typed_dict(MyDict, {"a": 1}) is False


def test_annotated_with_helper_gt():
    @match_typing
    def inner(val: Annotated[int, Gt(0)]):
        pass

    inner(1)
    with pytest.raises(TypeMismatch):
        inner(0)
    with pytest.raises(TypeMismatch):
        inner(-1)


def test_annotated_with_helper_gte():
    @match_typing
    def inner(val: Annotated[int, Gte(0)]):
        pass

    inner(1)
    inner(0)
    with pytest.raises(TypeMismatch):
        inner(-1)


def test_annotated_with_helper_lt():
    @match_typing
    def inner(val: Annotated[int, Lt(0)]):
        pass

    inner(-1)
    with pytest.raises(TypeMismatch):
        inner(0)
    with pytest.raises(TypeMismatch):
        inner(1)


def test_annotated_with_helper_lte():
    @match_typing
    def inner(val: Annotated[int, Lte(0)]):
        pass

    inner(-1)
    inner(0)
    with pytest.raises(TypeMismatch):
        inner(1)


def test_annotated_with_helper_range():
    @match_typing
    def inner(val: Annotated[int, Range(0, 10)]):
        pass

    inner(0)
    inner(5)
    inner(10)
    with pytest.raises(TypeMismatch):
        inner(-1)
    with pytest.raises(TypeMismatch):
        inner(11)


def test_annotated_with_helper_positive():
    @match_typing
    def inner(val: Annotated[int, IsPositive()]):
        pass

    inner(1)
    with pytest.raises(TypeMismatch):
        inner(0)
    with pytest.raises(TypeMismatch):
        inner(-1)


def test_annotated_with_helper_negative():
    @match_typing
    def inner(val: Annotated[int, IsNegative()]):
        pass

    inner(-1)
    with pytest.raises(TypeMismatch):
        inner(0)
    with pytest.raises(TypeMismatch):
        inner(1)


def test_annotated_with_helper_uuid():
    @match_typing
    def inner(val: Annotated[str, IsUUid()]):
        pass

    inner("550e8400-e29b-41d4-a716-446655440000")
    with pytest.raises(TypeMismatch):
        inner("not-a-uuid")


def test_annotated_with_helper_len():
    @match_typing
    def inner(val: Annotated[str, Len(lower=1, upper=3)]):
        pass

    inner("a")
    inner("abc")
    with pytest.raises(TypeMismatch):
        inner("")
    with pytest.raises(TypeMismatch):
        inner("abcd")


def test_annotated_with_helper_regex():
    @match_typing
    def inner(val: Annotated[str, Regex(r"a+")]):
        pass

    inner("a")
    inner("aa")
    with pytest.raises(TypeMismatch):
        inner("b")
    with pytest.raises(TypeMismatch):
        inner("")
