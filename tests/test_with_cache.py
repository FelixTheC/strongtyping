#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 06.06.21
@author: felix
"""
import operator
import timeit
from functools import partial
from typing import List, Optional

import pytest

from strongtyping.strong_typing import match_class_typing, match_typing
from strongtyping.strong_typing_utils import TypeMismatch


def test_func_with_cache():
    @match_typing(cache_size=1)
    def foo(val_a: List[int], val_b: Optional[int] = 10):
        return list(map(partial(operator.mul, val_b), val_a))

    for i in range(10):
        assert foo([1, 2, 3, 4, 5, 6, 7, 8]) == [10, 20, 30, 40, 50, 60, 70, 80]

    assert foo([1, 2, 3, 4, 5, 6, 7, 9]) == [10, 20, 30, 40, 50, 60, 70, 90]

    assert foo([2, 4, 6, 8], 2) == [4, 8, 12, 16]

    with pytest.raises(TypeMismatch):
        foo([1, 2, 3, 4, 5, 6, 7, "8"])
        foo([1, 2, 3, 4, "hello error", 6, 7, 9])
        foo([2, 4, 6, 8], "2")


def test_class_with_cache():
    @match_class_typing(cache_size=1)
    class MyClass:
        def foo(self, val_a: List[int], val_b: Optional[int] = 10):
            return list(map(partial(operator.mul, val_b), val_a))

    my_class = MyClass()

    for i in range(10):
        assert my_class.foo([1, 2, 3, 4, 5, 6, 7, 8]) == [10, 20, 30, 40, 50, 60, 70, 80]

    assert my_class.foo([1, 2, 3, 4, 5, 6, 7, 9]) == [10, 20, 30, 40, 50, 60, 70, 90]

    assert my_class.foo([2, 4, 6, 8], 2) == [4, 8, 12, 16]

    with pytest.raises(TypeMismatch):
        my_class.foo([1, 2, 3, 4, "5", 6, 7, 8])
        my_class.foo([1, 2, 3, 4, 5, 6, 7, "9"])
        my_class.foo([2, 4, 6, 8], "2")


@match_typing(cache_size=0)
def foo(val_a: List[int], val_b: Optional[int] = 10):
    return list(map(partial(operator.mul, val_b), val_a))


@match_typing(cache_size=1)
def foo_cached(val_a: List[int], val_b: Optional[int] = 10):
    return list(map(partial(operator.mul, val_b), val_a))


@match_class_typing(cache_size=0)
class MyClass:
    def foo(self, val_a: List[int], val_b: Optional[int] = 10):
        return list(map(partial(operator.mul, val_b), val_a))


@match_class_typing(cache_size=1)
class MyClassCached:
    def foo(self, val_a: List[int], val_b: Optional[int] = 10):
        return list(map(partial(operator.mul, val_b), val_a))


data_1 = list(range(100))


def test_cache_enabled_will_boost():
    assert timeit.timeit("foo(data_1)", globals=globals(), number=1000) > timeit.timeit(
        "foo_cached(data_1)", globals=globals(), number=1000
    )

    assert timeit.timeit("foo(data_1, 10)", globals=globals(), number=1000) > timeit.timeit(
        "foo_cached(data_1, 10)", globals=globals(), number=1000
    )

    assert timeit.timeit("MyClass().foo(data_1)", globals=globals(), number=1000) > timeit.timeit(
        "MyClassCached().foo(data_1)", globals=globals(), number=1000
    )

    assert timeit.timeit(
        "MyClass().foo(data_1, 10)", globals=globals(), number=1000
    ) > timeit.timeit("MyClassCached().foo(data_1, 10)", globals=globals(), number=1000)


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
