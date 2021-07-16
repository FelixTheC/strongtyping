#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from strongtyping.types import FrozenType


def test_create_class_with_final_types():
    class A:
        foo = FrozenType(int)
        bar = FrozenType(str)

        def __init__(self, val: foo, val_b: bar):
            self.foo = val
            self.bar = val_b

    class_a = A(10, "lorem ipsum")

    assert class_a.foo == 10
    assert class_a.bar == "lorem ipsum"

    with pytest.raises(TypeError):
        class_a.foo = 5.0
        class_a.bar = class_a.bar.split()


def test_cast_a_final_type():
    class A:
        foo = FrozenType(int)
        bar = FrozenType(int)

        def __init__(self, val: foo, val_b: bar):
            self.foo = val
            self.bar = val_b

        def to_float(self):
            self.foo = FrozenType.cast(self, self.foo, float)

    class_a = A(10, 1)
    class_a.to_float()
    class_a.foo = 5.0

    assert isinstance(class_a.foo, float)
    assert class_a.foo == 5.0

    with pytest.raises(TypeError):
        class_a.foo = 100
        class_a.bar = 21.5


def test_independent_classes():
    class A:
        attr_a = FrozenType(list)

        def __init__(self):
            self.attr_a = list(range(10))

    class B:
        attr_a = FrozenType(tuple)

        def __init__(self):
            self.attr_a = ("Hello", "World")

    a = A()
    b = B()

    assert a.attr_a == list(range(10))
    assert b.attr_a == ("Hello", "World")

    with pytest.raises(TypeError):
        a.attr_a, b.attr_a = b.attr_a, a.attr_a


def test_inheritance():
    class Base:
        attr_a = FrozenType(dict)

        def __init__(self):
            self.attr_a = {"foo": "bar"}

    class Child(Base):
        pass

    child = Child()
    child.attr_a = {"jon": "doe"}

    with pytest.raises(TypeError):
        child.attr_a = {"foo", "bar"}


def test_not_builtin():
    class Foo:
        pass

    class Bar:
        pass

    class A:
        attr_a = FrozenType(Bar)

        def __init__(self):
            self.attr_a = Bar()

    a = A()

    assert isinstance(a.attr_a, Bar)

    with pytest.raises(TypeError):
        a.attr_a = Foo()


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
