#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 24.05.21
@author: felix
"""
import decimal
import fractions
import os
import sys
from functools import partial
from typing import Dict, Iterable, List, Tuple, Union

import pytest

from strongtyping.strong_typing import TypeMismatch, match_class_typing, match_typing
from strongtyping.strong_typing_utils import ValidationError
from strongtyping.types import IterValidator, Validator


def test_valid_type():
    @match_typing
    def foo(val_a: Validator[list, lambda x: len(x) > 2]):
        return True

    assert foo([1, 2, 3])

    with pytest.raises(ValidationError):
        foo([1, 2])

    with pytest.raises(ValidationError):
        foo(
            [
                1,
            ]
        )

    with pytest.raises(TypeMismatch):
        foo({1, 2, 3})

    def min_length(val):
        return len(val) > 2

    @match_typing
    def foo(val_a: Validator[List[int], min_length]):
        return True

    assert foo([1, 2, 3])

    with pytest.raises(ValidationError):
        foo([1, 2])

    with pytest.raises(ValidationError):
        foo(
            [
                1,
            ]
        )

    with pytest.raises(TypeMismatch):
        foo(["1", "2", "3"])

    with pytest.raises(TypeMismatch):
        foo((1, 2, 3))

    def min_length(val, *, size):
        return len(val) >= size

    @match_typing
    def foo(
        val_a: Validator[
            Dict[Union[str, int], Union[List[int], Tuple[int, ...]]],
            partial(min_length, size=2),
        ]
    ):
        return True

    assert foo({2: [2, 4], "hello": (2, 3, 4, 5)})

    with pytest.raises(ValidationError):
        foo({2: [2, 4]})


@pytest.mark.skipif(
    bool(int(os.environ["ST_MODULES_INSTALLED"])) is True,
    reason="module does not support Validator at the moment",
)
@pytest.mark.skipif(sys.version_info.minor < 9, reason="Generics only available since 3.9")
def test_with_type_generics():
    def min_length(val):
        return len(val) > 2

    @match_typing
    def foo(val_a: Validator[list[int], min_length]):
        return True

    assert foo([1, 2, 3])

    with pytest.raises(ValidationError):
        foo([1, 2])

    with pytest.raises(ValidationError):
        foo(
            [
                1,
            ]
        )

    with pytest.raises(TypeMismatch):
        foo(["1", "2", "3"])

    with pytest.raises(TypeMismatch):
        foo((1, 2, 3))

    def min_length(val, *, size):
        return len(val) >= size

    @match_typing
    def foo(
        val_a: Validator[
            dict[Union[str, int], Union[list[int], tuple[int, ...]]],
            partial(min_length, size=2),
        ]
    ):
        return True

    assert foo({2: [2, 4], "hello": (2, 3, 4, 5)})

    with pytest.raises(ValidationError):
        foo({2: [2, 4]})

    with pytest.raises(TypeMismatch):
        foo(((1, 2), (3, 4)))


def test_inside_of_a_class():
    def min_length(val):
        return all(len(data) >= 5 for data in val)

    @match_class_typing
    class Foo:
        def method_a(self, bar: Validator[Tuple[str, str], min_length]):
            return True

    foo = Foo()

    assert foo.method_a(("Hello", "World"))
    with pytest.raises(ValidationError):
        assert foo.method_a(("Hello", "Char"))

    with pytest.raises(ValidationError):
        assert foo.method_a(("Hi", "Hi"))

    with pytest.raises(TypeMismatch):
        assert foo.method_a(())


@pytest.mark.skipif(
    bool(int(os.environ["ST_MODULES_INSTALLED"])) is True,
    reason="module does not support Validator at the moment",
)
@pytest.mark.skipif(sys.version_info.minor < 9, reason="Available since 3.9")
def test_validator_type_with_default():
    @match_typing
    def foo(val_a: Validator[list, lambda x: len(x) > 2, []]):
        return True

    assert foo([1, 2, 3])

    assert foo([1, 2]) == []

    assert (
        foo(
            [
                1,
            ]
        )
        == []
    )

    with pytest.raises(TypeMismatch):
        foo({1, 2, 3})

    def min_length(val):
        return len(val) > 2

    @match_typing
    def foo(val_a: Validator[List[int], min_length, None]):
        return True

    assert foo([1, 2, 3])
    assert foo([1, 2]) is None
    assert (
        foo(
            [
                1,
            ]
        )
        is None
    )

    with pytest.raises(TypeMismatch):
        foo(["1", "2", "3"])

    with pytest.raises(TypeMismatch):
        foo((1, 2, 3))

    def min_length(val, *, size):
        return len(val) >= size

    @match_typing
    def foo(
        val_a: Validator[
            Dict[Union[str, int], Union[List[int], Tuple[int, ...]]],
            partial(min_length, size=2),
        ]
    ):
        return True

    assert foo({2: [2, 4], "hello": (2, 3, 4, 5)})

    with pytest.raises(ValidationError):
        foo({2: [2, 4]})

    with pytest.raises(TypeError):
        AllowedCluster = Validator[Iterable[Union[int, fractions.Fraction, decimal.Decimal]]]


@pytest.mark.skipif(sys.version_info.minor < 9, reason="Available since 3.9")
def test_iter_validator():
    number = Union[int, fractions.Fraction, decimal.Decimal]

    def allow_only_int_dec_frac(value: number):
        if not value % 1 == 0:
            raise TypeError
        return True

    AllowedCluster = IterValidator[Iterable[number], allow_only_int_dec_frac]

    @match_typing
    def cluster(val: AllowedCluster):
        return True

    with pytest.raises(TypeMismatch):
        cluster((1, 2, 3.5))  # non int float
        cluster([1, 2, "abc"])  # non int str
        cluster([1, 2, "3.5"])  # non int str
        cluster([1, 2, decimal.Decimal("2.1")])  # not int decimal
        cluster([1, 2, fractions.Fraction(3, 2)])  # non int fraction


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
