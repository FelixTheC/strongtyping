#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 03.06.21
@author: felix
"""
import sys
from typing import List, NotRequired, Required, TypedDict, Union, Unpack

import pytest

from strongtyping.strong_typing import match_class_typing, match_typing
from strongtyping.strong_typing_utils import TypeMismatch, UndefinedKey, ValidationError


def test_typedict():
    from typing import TypedDict

    @match_class_typing
    class SalesSummary(TypedDict):
        sales: int
        country: str
        product_codes: List[str]

    assert SalesSummary({"sales": 10, "country": "Foo", "product_codes": ["1", "2", "3"]})

    with pytest.raises(TypeMismatch):
        SalesSummary({"sales": "Foo", "country": 10, "product_codes": [1, 2, 3]})


def test_typedict_with_total():
    from typing import TypedDict

    @match_class_typing
    class SalesSummary(TypedDict, total=False):
        sales: int
        country: str
        product_codes: List[str]

    assert SalesSummary({"sales": 10, "product_codes": ["1", "2", "3"]})

    with pytest.raises(TypeMismatch):
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

    with pytest.raises(TypeMismatch):
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

    with pytest.raises(TypeMismatch):
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

    with pytest.raises(TypeMismatch):
        move_to({"x": 1.0, "y": 2})
    with pytest.raises(TypeMismatch):
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

    with pytest.raises(TypeMismatch):
        make_move({"position": {"x": 1.0, "y": 2.0, "z": "0.25"}, "velocity": 1.0})

    with pytest.raises(TypeMismatch):
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


def test_typeddict_with_required():
    from typing import TypedDict

    @match_class_typing
    class Movie(TypedDict, total=False):
        title: Required[str]
        year: int

    new_obj = Movie(title="Prisoner of azkaban")
    assert new_obj


def test_typeddict_with_not_required():
    from typing import TypedDict

    @match_class_typing
    class Movie(TypedDict):  # implicitly total=True
        title: str
        year: NotRequired[int]

    new_obj = Movie(title="Prisoner of azkaban")
    assert new_obj


def test_typeddict_with_required_and_not_required():
    from typing import TypedDict

    @match_class_typing
    class Movie(TypedDict):
        title: Required[str]  # redundant
        year: NotRequired[int]

    new_obj = Movie(title="Prisoner of azkaban")
    assert new_obj

    new_obj = Movie(title="Prisoner of azkaban", year=2004)
    assert new_obj


def test_typeddict_with_not_required_required_fails():
    from typing import TypedDict

    @match_class_typing
    class Movie(TypedDict):
        title: str
        year: NotRequired[NotRequired[Required[int]]]

    with pytest.raises(TypeError):
        Movie(title="Prisoner of azkaban")


def test_typeddict_with_not_required_cannot_before_required():
    from typing import TypedDict

    @match_class_typing
    class Movie(TypedDict):
        year: NotRequired[int]
        title: str

    with pytest.raises(TypeError):
        Movie(title="Prisoner of azkaban")

    @match_class_typing
    class Movie(TypedDict):
        title: str
        regisseur: Required[str]
        month: NotRequired[int]
        year: Required[int]

    with pytest.raises(TypeError):
        Movie(title="Prisoner of azkaban", regisseur="Alfonso Cuarón", year=2004)


def test_typeddict_with_required_and_not_required_and_sub_typeddict():
    @match_class_typing
    class Movie(TypedDict):
        title: str
        year: NotRequired[int]

    @match_class_typing
    class Additional(TypedDict):
        name: str
        val: NotRequired[str]

    @match_class_typing
    class Regisseur(TypedDict):
        name: str
        movie: Required[dict[Movie]]
        year: Required[int]
        info: NotRequired[dict[Additional]]

    assert Regisseur(name="Alfonso Cuarón", movie=Movie(title="Hallow"), year=2004)

    with pytest.raises(TypeMismatch):
        Regisseur(name="Alfonso Cuarón", movie=Movie, year=2004)

    with pytest.raises(TypeMismatch):
        Regisseur(name="Alfonso Cuarón", year=2004)


def test_unpacking():
    @match_class_typing
    class Additional(TypedDict):
        name: str
        val: NotRequired[str]

    class Regisseur(TypedDict):
        name: str
        info: NotRequired[dict[Additional]]

    class Movie(TypedDict):
        name: str
        year: int
        regisseur: Regisseur

    @match_typing
    def foo(**kwargs: Unpack[Movie]) -> str:
        return f"{kwargs['year']}: {kwargs['name']}"

    with pytest.raises(TypeMismatch):
        foo(name="foobar", date=2023)

    movie = Movie(name="Alfonso Cuarón", year=2004, regisseur=Regisseur(name="foobar"))
    foo(**movie)


def test_undefined_keys_raise_error():
    @match_class_typing(throw_on_undefined=True)
    class User(TypedDict):
        id: str
        username: str
        description: str | None

    with pytest.raises(UndefinedKey):
        User({"id": "0123", "username": "test", "description": None, "age": 10})

    with pytest.raises(UndefinedKey):
        User(id="Alfonso Cuarón", username="2004", description=None, age=10)

    assert User({"id": "0123", "username": "test", "description": None})
    assert User(id="0123", username="test")


@pytest.mark.skipif(
    sys.version_info.minor < 13, reason="TypedDict ReadOnly option available since 3.13"
)
def test_readonly_is_ignored():
    from typing import ReadOnly

    @match_class_typing
    class User(TypedDict):
        id: ReadOnly[str]
        username: str
        description: str | None

    assert User({"id": "0123", "username": "test", "description": None})
    assert User(id="0123", username="test")


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
