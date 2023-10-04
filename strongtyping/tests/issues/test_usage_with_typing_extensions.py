from typing import NotRequired, Required, TypedDict

import pytest

from strongtyping.strong_typing import match_class_typing


def test_nested_typed_dicts():
    @match_class_typing
    class ChildType(TypedDict):
        key_a: int
        key_b: int

    @match_class_typing
    class ParentType(TypedDict):
        child: ChildType
        not_required: NotRequired[int]

    parent = {"child": {"key_a": 1, "key_b": 2}}
    ParentType(parent)


def test_not_required():
    @match_class_typing
    class ChildType(TypedDict):
        key_a: int
        key_b: int

    @match_class_typing
    class ParentType(TypedDict):
        child: ChildType
        not_required: NotRequired[int]

    parent = {"not_required": 3, "child": {"key_a": 1, "key_b": 2}}
    ParentType(parent)


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])