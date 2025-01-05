#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 09.07.20
@author: eisenmenger
"""
import pytest

from strongtyping.docstring_typing import getter_setter as dt_getter_setter, setter as dt_setter
from strongtyping.strong_typing import TypeMismatch, getter_setter, setter


class Dummy:
    attr = 100
    val = "foo"

    @setter
    def b(self, val: str):
        self.val = val

    @getter_setter
    def c(self, val: int = None):
        if val is not None:
            self.attr = val
        return self.attr


class DummyDocStr:
    attr = 100
    val = "foo"

    @dt_setter
    def b(self, val):
        """
        :param str val:
        """
        self.val = val

    @dt_getter_setter
    def c(self, val=None):
        """
        :type val: int
        """
        if val is not None:
            self.attr = val
        return self.attr


def test_setter():
    d = Dummy()
    with pytest.raises(AttributeError):
        assert d.b == "foo"

    d.b = "bar"
    assert d.val == "bar"

    with pytest.raises(TypeMismatch):
        d.b = 1

    dd = DummyDocStr()
    with pytest.raises(AttributeError):
        assert dd.b == "foo"

    dd.b = "bar"
    assert dd.val == "bar"

    with pytest.raises(TypeMismatch):
        dd.b = 1


def test_getter_setter():
    d = Dummy()
    assert d.c == 100
    with pytest.raises(TypeMismatch):
        d.c = "10"
    d.c = 10
    assert d.c == 10

    dd = DummyDocStr()
    assert dd.c == 100
    with pytest.raises(TypeMismatch):
        dd.c = "10"
    dd.c = 10
    assert dd.c == 10


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
