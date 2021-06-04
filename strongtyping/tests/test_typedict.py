#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 03.06.21
@author: felix
"""
import sys
from typing import List

import pytest

from strongtyping.strong_typing import match_class_typing, match_typing
from strongtyping.strong_typing_utils import TypeMisMatch, ValidationError


@pytest.mark.skipif(sys.version_info.minor < 8, reason="TypedDict only available since 3.8")
def test_typedict():
    from typing import TypedDict

    @match_class_typing
    class SalesSummary(TypedDict):
        sales: int
        country: str
        product_codes: List[str]

    assert SalesSummary({"sales": 10, "country": "Foo", "product_codes": ["1", "2", "3"]})

    with pytest.raises(TypeMisMatch):
        SalesSummary({"sales": "Foo", "country": 10, "product_codes": [1, 2, 3]})


@pytest.mark.skipif(sys.version_info.minor < 8, reason="TypedDict only available since 3.8")
def test_typedict_with_total():
    from typing import TypedDict

    @match_class_typing
    class SalesSummary(TypedDict, total=False):
        sales: int
        country: str
        product_codes: List[str]

    assert SalesSummary({"sales": 10, "product_codes": ["1", "2", "3"]})

    with pytest.raises(TypeMisMatch):
        SalesSummary({"sales": "Foo", "product_codes": [1, 2, 3]})


@pytest.mark.skipif(sys.version_info.minor < 8, reason="TypedDict only available since 3.8")
def test_typedict_with_validator():
    from typing import TypedDict
    from strongtyping.types import Validator

    @match_class_typing
    class MyDict(TypedDict):
        sales: int
        country: str
        product_codes: List[str]

    def allow_only_valid_country_names(value: MyDict):
        return not value["country"].isnumeric()

    AllowedDicts = Validator[MyDict, allow_only_valid_country_names]

    @match_typing
    def cluster(val: AllowedDicts):
        return True

    assert cluster({"sales": 10, "country": "Europe", "product_codes": "Hello World".split()})

    with pytest.raises(ValidationError):
        cluster({"sales": 10, "country": "123456789", "product_codes": "Hello World".split()})

    with pytest.raises(TypeMisMatch):
        cluster({"sales": "10", "country": "Europe", "product_codes": "Hello World".split()})
        cluster({"sales": 10, "country": "Europe", "product_codes": list(range(10))})


@pytest.mark.skipif(sys.version_info.minor < 8, reason="TypedDict only available since 3.8")
def test_typedict_with_validator_and_total():
    from typing import TypedDict
    from strongtyping.types import Validator

    @match_class_typing
    class MyDict(TypedDict, total=False):
        sales: int
        country: str
        product_codes: List[str]

    def allow_only_valid_country_names(value: MyDict):
        return not value.get("country", "").isnumeric()

    AllowedDicts = Validator[MyDict, allow_only_valid_country_names]

    @match_typing
    def cluster(val: AllowedDicts):
        return True

    assert cluster({"sales": 10, "product_codes": "Hello World".split()})

    with pytest.raises(ValidationError):
        cluster({"country": "123456789", "product_codes": "Hello World".split()})

    with pytest.raises(TypeMisMatch):
        cluster({"sales": "10", "country": "Europe"})
        cluster({"product_codes": list(range(10))})


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
