"""
@created: 12.02.23
@author: felix
"""

from dataclasses import dataclass, field

import pytest

from strongtyping.strong_typing import match_class_typing
from strongtyping.strong_typing_utils import TypeMismatch


def test_create_instance():
    @match_class_typing
    @dataclass
    class MyType:
        value: float = None

        def method(self):
            pass

    req = MyType(2.3)
    assert req is not None
    assert req.value == 2.3


def test_call_method():
    @match_class_typing
    @dataclass()
    class MyType:
        value: float = None

        def method(self):
            pass

    req = MyType(2.3)
    assert req.method() is None


def test_dataclass_with_function_annotation():
    @match_class_typing
    @dataclass
    class D:
        x: list = field(default_factory=list)

        def add(self, element: list[int]):
            self.x += element

    datacls = D()
    assert datacls is not None

    with pytest.raises(TypeMismatch):
        datacls.add("2")

    with pytest.raises(TypeMismatch):
        datacls.add(["2"])

    datacls.add([2])
    assert datacls.x == [2]


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
