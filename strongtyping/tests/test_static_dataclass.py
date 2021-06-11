#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dataclasses

import pytest

from strongtyping.strong_typing import static_dataclass


def test_attributes_are_not_changable():

    @dataclasses.dataclass
    class B:
        val_a: int
        val_b: str
        val_c: list
        val_d: dict

    @static_dataclass
    class A:
        val_a: int
        val_b: str
        val_c: list
        val_d: dict

    a = A(1, "2", val_c=[4, 5], val_d={6: "7"})
    b = B(1, "2", val_c=[4, 5], val_d={6: "7"})

    # this is what the static_dataclass decorator should prevent
    b.val_a = b.val_d
    assert b.val_a == b.val_d
    assert not isinstance(b.val_a, int)

    assert a.val_a == 1
    assert a.val_b == "2"
    assert a.val_c == [4, 5]
    assert a.val_d == {6: "7"}

    with pytest.raises(TypeError):
        a.val_a = a.val_b
        a.val_c = a.val_d
        

if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
