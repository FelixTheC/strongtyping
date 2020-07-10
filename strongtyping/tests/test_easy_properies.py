#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 09.07.20
@author: eisenmenger
"""
import pytest

from strongtyping.easy_property import getter
from strongtyping.strong_typing import getter_setter
from strongtyping.strong_typing import setter
from strongtyping.strong_typing import TypeMisMatch


class Dummy:
    attr = 100
    val = 'foo'

    @getter
    def a(self):
        return self.attr

    @setter
    def b(self, val: str):
        self.val = val

    @getter_setter
    def c(self, val: int = None):
        if val is not None:
            self.attr = val
        return self.attr


def test_getter():
    d = Dummy()
    assert d.a == 100
    with pytest.raises(AttributeError):
        d.a = 10


def test_setter():
    d = Dummy()
    with pytest.raises(AttributeError):
        assert d.b == 'foo'

    d.b = 'bar'
    assert d.val == 'bar'

    with pytest.raises(TypeMisMatch):
        d.b = 1


def test_getter_setter():
    d = Dummy()
    assert d.c == 100
    with pytest.raises(TypeMisMatch):
        d.c = '10'
    d.c = 10
    assert d.c == 10


if __name__ == '__main__':
    pytest.main(['-v', '-s', __file__])
