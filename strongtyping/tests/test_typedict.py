#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 03.06.21
@author: felix
"""
from typing import List, TypedDict

import pytest

from strongtyping.strong_typing import match_class_typing
from strongtyping.strong_typing_utils import TypeMisMatch


def test_typedict():
    @match_class_typing
    class SalesSummary(TypedDict):
        sales: int
        country: str
        product_codes: List[str]

    assert SalesSummary({"sales": 10, "country": "Foo", "product_codes": ["1", "2", "3"]})

    with pytest.raises(TypeMisMatch):
        SalesSummary({"sales": "Foo", "country": 10, "product_codes": [1, 2, 3]})


def test_typedict_with_total():
    #  total=False
    @match_class_typing
    class SalesSummary(TypedDict, total=False):
        sales: int
        country: str
        product_codes: List[str]

    assert SalesSummary({"sales": 10, "product_codes": ["1", "2", "3"]})

    with pytest.raises(TypeMisMatch):
        SalesSummary({"sales": "Foo", "product_codes": [1, 2, 3]})


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
