#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from strongtyping.types import FinalType


def test_create_class_with_final_types():
    class A:
        foo = FinalType(int)
        bar = FinalType(str)

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
        foo = FinalType(int)
        bar = FinalType(int)

        def __init__(self, val: foo, val_b: bar):
            self.foo = val
            self.bar = val_b

        def to_float(self):
            self.foo = FinalType.cast(self.foo, float)

    class_a = A(10, 1)
    class_a.to_float()
    class_a.foo = 5.0

    assert isinstance(class_a.foo, float)
    assert class_a.foo == 5.0

    with pytest.raises(TypeError):
        class_a.foo = 10


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
