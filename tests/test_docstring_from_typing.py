#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 16.05.21
@author: felix
"""
import decimal
import sys
from typing import List, Tuple, Union

try:
    from typing import Literal
except ImportError:
    print("python version < 3.8")

import pytest

from strongtyping.docs_from_typing import (
    class_docs_from_typing,
    numpy_docs_from_typing,
    rest_docs_from_typing,
)


@pytest.mark.skipif(
    sys.version_info.minor < 9, reason='"type" object subscribable available in py3.9'
)
def test_rest_docstring_from_typing():
    @rest_docs_from_typing
    def foo(val_a: int, val_b: list[str], val_c: Tuple[str, ...], *args, **kwargs) -> None:
        pass

    class Foo:
        @rest_docs_from_typing
        def foo(self, val_a: int, val_b: list[str]):
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__


@pytest.mark.skipif(
    sys.version_info.minor < 9, reason='"type" object subscribable available in py3.9'
)
def test_numpy_docstring_from_typing():
    @numpy_docs_from_typing
    def foo(
        val_a: int, val_b: list[str], val_c: Tuple[str, ...], *args, **kwargs
    ) -> Union[int, float]:
        pass

    class Foo:
        @numpy_docs_from_typing
        def foo(self, val_a: int, val_b: list[str]) -> Tuple[str, ...]:
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__


def test_rest_docstring_from_typing_2():
    @rest_docs_from_typing
    def foo(
        val_a: int,
        val_b: List[Union[int, float, decimal.Decimal]],
        val_c: Tuple[str, ...],
        *args,
        **kwargs,
    ):
        pass

    class Foo:
        @rest_docs_from_typing
        def foo(self, val_a: int, val_b: Tuple[str, ...]):
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__


def test_numpy_docstring_from_typing_2():
    @numpy_docs_from_typing
    def foo(
        val_a: int,
        val_b: List[Union[int, float, decimal.Decimal]],
        val_c: Tuple[str, ...],
        *args,
        **kwargs,
    ):
        pass

    class Foo:
        @numpy_docs_from_typing
        def foo(self, val_a: int, val_b: Tuple[str, ...]):
            pass

    assert foo.__doc__
    assert Foo.foo.__doc__


@pytest.mark.skipif(sys.version_info.minor < 8, reason="Literal first available in py3.8")
def test_rest_docstring_from_typing_literal():
    @rest_docs_from_typing
    def foo(val_a: Literal["jon", "doe"]):
        pass

    assert foo.__doc__


@pytest.mark.skipif(sys.version_info.minor < 8, reason="Literal first available in py3.8")
def test_numpy_docstring_from_typing_literal():
    @numpy_docs_from_typing
    def foo(val_a: Literal["jon", "doe"]):
        pass

    assert foo.__doc__


def test_docstring_on_whole_class():
    @class_docs_from_typing
    class Foo:
        def __init__(self, val_a: int, val_b: Tuple[str, ...]):
            pass

    assert Foo.__doc__
    assert "val_a" in Foo.__doc__
    assert "val_b" in Foo.__doc__
