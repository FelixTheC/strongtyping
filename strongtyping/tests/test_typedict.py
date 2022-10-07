#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 03.06.21
@author: felix
"""
from typing import List, Union

import pytest

from strongtyping.strong_typing import match_class_typing, match_typing
from strongtyping.strong_typing_utils import TypeMisMatch, ValidationError


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


def test_use_typed_dict_total_true_class_as_function_parameter_to_validate():
    from typing import TypedDict

    class Point(TypedDict):
        x: float
        y: float

    @match_typing
    def move_to(pos: Point):
        print(f'moving to ({pos["x"]}, {pos["y"]})')
        return True

    assert move_to({"x": 1.0, "y": 2.2})

    with pytest.raises(TypeMisMatch):
        move_to({"x": 1.0, "y": 2})
    with pytest.raises(TypeMisMatch):
        move_to({"y": 2.1})


def test_use_typed_dict_total_false_class_as_function_parameter_to_validate():
    from typing import TypedDict

    class Vector(TypedDict, total=False):
        x: float
        y: float
        z: float

    @match_typing
    def move_to(pos: Vector):
        print(f'moving to ({pos.get("x", 1.0)}, {pos.get("y", 1.0)}, {pos.get("z", 1)})')
        return True

    assert move_to({})
    assert move_to({"x": 1.0, "y": 2.0})


def test_nested_typeddicts():
    from typing import TypedDict

    class Vector(TypedDict, total=False):
        x: float
        y: float
        z: float

    class Move(TypedDict):
        position: Vector
        velocity: Union[float, int]

    @match_typing
    def make_move(move: Move):
        return True

    assert make_move({"position": {"x": 1.0, "y": 2.0, "z": 0.25}, "velocity": 1.0})
    assert make_move({"position": {"x": 1.0, "z": 0.25}, "velocity": 1.0})
    assert make_move({"position": {"x": 1.0, "y": 2.0, "z": 0.25}, "velocity": 1})

    with pytest.raises(TypeMisMatch):
        make_move({"position": {"x": 1.0, "y": 2.0, "z": "0.25"}, "velocity": 1.0})

    with pytest.raises(TypeMisMatch):
        make_move({"position": {"x": 1.0, "y": 2.0, "z": 0.25}})


def test_calling_a_typeddict_class_without_dict():
    from typing import TypedDict

    @match_class_typing
    class Example(TypedDict):
        x: float
        y: float
        z: float

    new_obj = Example(x=1.0, y=2.0, z=3.0)
    assert new_obj


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
