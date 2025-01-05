#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 26.06.21
@author: felix
"""
import pytest

from strongtyping.strong_typing import match_class_typing, match_typing
from strongtyping.strong_typing_utils import TypeMismatch


def test_correct_repr():
    repr_of_original_foo = ""

    class Foo:
        def __init__(self, val: int):
            self.val = val

    repr_of_original_foo = repr(Foo)

    @match_class_typing
    class Foo:
        def __init__(self, val: int):
            self.val = val

    assert repr_of_original_foo == repr(Foo)


def test_correct_str():
    str_of_original_foo = ""

    class Foo:
        def __init__(self, val: int):
            self.val = val

    str_of_original_foo = str(Foo)

    @match_class_typing
    class Foo:
        def __init__(self, val: int):
            self.val = val

    assert str_of_original_foo == str(Foo)


def test_wrong_type_for_classes_decorated_with_match_class_typing():
    class Foo:
        def __init__(self, val: int):
            self.val = val

    @match_typing
    def bar(value: Foo):
        pass

    bar(Foo(10))
    with pytest.raises(TypeMismatch):
        bar("10")

    @match_class_typing
    class Foo:
        def __init__(self, val: int):
            self.val = val

    @match_typing
    def bar(value: Foo):
        pass

    my_foo = Foo(10)
    bar(my_foo)
    with pytest.raises(TypeMismatch):
        bar("10")


def test_class_decorated_class_isinstance_is_proberly_working():
    @match_class_typing
    class Foo:
        def __init__(self, val: int = 10):
            self.val = val

    foo = Foo()
    assert isinstance(foo, Foo)


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
