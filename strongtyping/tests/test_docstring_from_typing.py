#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 16.05.21
@author: felix
"""
from typing import Tuple

from strongtyping.docs_from_typing import rest_docs_from_typing, numpy_docs_from_typing


def test_rest_docstring_from_typing():

    @rest_docs_from_typing
    def foo(val_a: int, val_b: list[str], val_c: Tuple[str, ...], *args, **kwargs):
        pass

    class Foo:

        @rest_docs_from_typing
        def foo(self, val_a: int, val_b: list[str]):
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__


def test_numpy_docstring_from_typing():

    @numpy_docs_from_typing
    def foo(val_a: int, val_b: list[str], val_c: Tuple[str, ...], *args, **kwargs):
        pass

    class Foo:

        @numpy_docs_from_typing
        def foo(self, val_a: int, val_b: list[str]):
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__

