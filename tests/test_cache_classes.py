#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 12.07.20
@author: felix
"""
import pytest

from strongtyping.cached_dict import CachedDict
from strongtyping.cached_set import CachedSet


@pytest.mark.parametrize("cls", [CachedDict, CachedSet])
def test_max_size(cls):
    def _add(memory_limit, max_items: int = 10):
        cached_dict = cls(memory_limit=memory_limit)
        for i in range(max_items):
            val = ("helloworld" * i).split()
            try:
                cached_dict[str(i)] = val
            except TypeError:
                cached_dict.add(val.__str__())
        return len(cached_dict)

    assert _add(memory_limit=0.0001) == 1
    assert _add(memory_limit=1, max_items=1000) == 1000
