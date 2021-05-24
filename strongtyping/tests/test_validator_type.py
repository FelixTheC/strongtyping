#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 24.05.21
@author: felix
"""
import sys
from functools import partial
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import pytest
from strongtyping.strong_typing import TypeMisMatch

from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import Validator


def test_valid_type():
    @match_typing
    def foo(val_a: Validator[list, lambda x: len(x) > 2]):
        return True

    assert foo([1, 2, 3])

    with pytest.raises(TypeMisMatch):
        foo([1, 2])

    with pytest.raises(TypeMisMatch):
        foo([1, ])

    def min_length(val):
        return len(val) > 2

    @match_typing
    def foo(val_a: Validator[List[int], min_length]):
        return True

    assert foo([1, 2, 3])

    with pytest.raises(TypeMisMatch):
        foo([1, 2])

    with pytest.raises(TypeMisMatch):
        foo([1, ])

    with pytest.raises(TypeMisMatch):
        foo(['1', '2', '3'])

    with pytest.raises(TypeMisMatch):
        foo((1, 2))

    def min_length(val, *, size):
        return len(val) >= size

    @match_typing
    def foo(val_a: Validator[Dict[Union[str, int], Union[List[int], Tuple[int, ...]]], partial(min_length, size=2)]):
        return True

    assert foo({2: [2, 4],
                'hello': (2, 3, 4, 5)})


@pytest.mark.skipif(sys.version_info.minor < 8, reason='Generics only available since 3.9')
def test_with_type_generics():

    def min_length(val):
        return len(val) > 2

    @match_typing
    def foo(val_a: Validator[list[int], min_length]):
        return True

    assert foo([1, 2, 3])

    with pytest.raises(TypeMisMatch):
        foo([1, 2])

    with pytest.raises(TypeMisMatch):
        foo([1, ])

    with pytest.raises(TypeMisMatch):
        foo(['1', '2', '3'])

    with pytest.raises(TypeMisMatch):
        foo((1, 2))

    def min_length(val, *, size):
        return len(val) >= size

    @match_typing
    def foo(val_a: Validator[dict[Union[str, int], Union[list[int], tuple[int, ...]]], partial(min_length, size=2)]):
        return True

    assert foo({2: [2, 4],
                'hello': (2, 3, 4, 5)})


if __name__ == '__main__':
    pytest.main(['-vv', '-s', __file__])
