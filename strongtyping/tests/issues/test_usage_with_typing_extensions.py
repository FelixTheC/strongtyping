import sys

import pytest

try:
    from typing_extensions import NotRequired, Required, TypedDict
except ImportError:
    from typing import TypedDict

    if sys.version_info.minor == 11:
        from typing import NotRequired, Required
    else:
        NotRequired = object()
        Required = object()

from strongtyping.strong_typing import match_class_typing
from strongtyping.strong_typing_utils import TypeMisMatch


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
