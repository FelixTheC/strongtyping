#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 16.06.20
@author: felix
"""
from datetime import datetime

import pytest

from docstring_typing import match_docstring
from strong_typing import TypeMisMatch


def test_simple_test_1():
    class Menu:
        pass

    @match_docstring
    def func_a(menu_definition, visible=None):
        """
        :param menu_definition: (New menu definition (in menu definition format)
        :type menu_definition: Menu
        :param visible: control visibility of element
        :type visible: bool
        """
        return datetime.today()

    assert func_a(Menu()) is not None
    assert func_a(Menu(), visible=False) is not None
    with pytest.raises(TypeMisMatch):
        func_a(datetime)
    with pytest.raises(TypeMisMatch):
        func_a(Menu(), 12)


def test_docstring_union():
    @match_docstring
    def func_a(a, b=None):
        """
        :type a: list, tuple
        :type b: bool
        """
        return True

    assert func_a([i for i in range(3)])
    assert func_a((1, 2, 3), b=True)
    with pytest.raises(TypeMisMatch):
        func_a(datetime)
    with pytest.raises(TypeMisMatch):
        func_a({'1', '2', '3'}, 12)


def test_docstring_tuple():
    @match_docstring
    def func_a(a, b=None):
        """
        :type a: (int, str, str)
        :type b: (str, (str, str))
        """
        return True

    assert func_a((1, 'hello', 'world'))
    assert func_a((2, 'foo', 'bar'), b=('jon', ('doe', 'doe')))
    with pytest.raises(TypeMisMatch):
        func_a(('hello', 'world'))
    with pytest.raises(TypeMisMatch):
        func_a((1, 'hello', 'world'), ('jon', 'doe'))


if __name__ == '__main__':
    @match_docstring
    def func_a(a, b=None):
        """
        :type a: (int, str, str)
        :type b: (str, (str, str))
        """
        return True

    func_a((2, 'foo', 'bar'), ('jon', ('doe', 'doe')))
    # pytest.main(['-vv', '-s', __file__])
