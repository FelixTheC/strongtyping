#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 16.05.21
@author: felix
"""
import decimal
import sys
from typing import Tuple, List, Union, Literal

import pytest

from strongtyping.docs_from_typing import rest_docs_from_typing, numpy_docs_from_typing


@pytest.mark.skipif(sys.version_info.minor < 9, reason='"type" object subscribable available in py3.9')
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


@pytest.mark.skipif(sys.version_info.minor < 9, reason='"type" object subscribable available in py3.9')
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


def test_rest_docstring_from_typing_2():

    @rest_docs_from_typing
    def foo(val_a: int, val_b: List[Union[int, float, decimal.Decimal]], val_c: Tuple[str, ...], *args, **kwargs):
        pass

    class Foo:

        @rest_docs_from_typing
        def foo(self, val_a: int, val_b: Tuple[str, ...]):
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__


def test_numpy_docstring_from_typing_2():

    @numpy_docs_from_typing
    def foo(val_a: int, val_b: List[Union[int, float, decimal.Decimal]], val_c: Tuple[str, ...], *args, **kwargs):
        pass

    class Foo:

        @numpy_docs_from_typing
        def foo(self, val_a: int, val_b: Tuple[str, ...]):
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__


@pytest.mark.skipif(sys.version_info.minor < 8, reason='Literal first available in py3.8')
def test_rest_docstring_from_typing_literal():

    @rest_docs_from_typing
    def foo(val_a: Literal['jon', 'doe']):
        pass

    assert foo.__doc__


@pytest.mark.skipif(sys.version_info.minor < 8, reason='Literal first available in py3.8')
def test_numpy_docstring_from_typing_literal():

    @numpy_docs_from_typing
    def foo(val_a: Literal['jon', 'doe']):
        pass

    assert foo.__doc__
