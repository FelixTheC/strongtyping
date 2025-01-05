#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 13.07.20
@author: felix
"""
import sys
from typing import Union

import pytest

if sys.version_info.minor >= 8:
    from strongtyping.type_namedtuple import typed_namedtuple

SKIP_MESSAGE = "Some features in typed_namedtuple are only available from version 3.8"

ContactBlockedHelper = typed_namedtuple("ContactBlockedHelper", [("allow", bool), ("block", bool)])


@pytest.fixture(scope="module")
def dummy_obj():
    return typed_namedtuple("Dummy", ["spell:str", "mana:int", "effect:list"])


def attr_of_obj_test(obj: type):
    for attr in (("spell", "Lumos"), ("mana", 5), ("effect", ["Makes light"])):
        assert getattr(obj, attr[0]) == attr[1]


def test_typed_namedtuple_no_type_returns_namedtuple():
    Dummy = typed_namedtuple("Dummy", ["spell", "mana", "effect"])
    assert (
        Dummy(
            spell="Lumos",
            mana=5,
            effect=[
                "Makes light",
            ],
        )
        is not None
    )


def test_typed_namedtuple_with_type_returns_object():
    Dummy = typed_namedtuple("Dummy", ["spell:str", "mana:int", "effect:list"])
    assert (
        Dummy(
            spell="Lumos",
            mana=5,
            effect=[
                "Makes light",
            ],
        )
        is not None
    )


def test_typed_namedtuple_with_type_returns_correct_val(dummy_obj):
    d = dummy_obj(
        spell="Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    attr_of_obj_test(d)

    d = dummy_obj(
        mana=5,
        effect=[
            "Makes light",
        ],
        spell="Lumos",
    )
    attr_of_obj_test(d)


def test_typed_namedtuple_instantiate_args_or_kwargs(dummy_obj):
    d = dummy_obj(
        "Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    attr_of_obj_test(d)

    d = dummy_obj(
        "Lumos",
        5,
        effect=[
            "Makes light",
        ],
    )
    attr_of_obj_test(d)


def test_typed_namedtuple_indexable(dummy_obj):
    d = dummy_obj(
        "Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    assert d[0] == "Lumos"
    assert d[-1] == ["Makes light"]
    assert d[1] == 5


def test_typed_namedtuple_unpack_like_regular_tuple(dummy_obj):
    d = dummy_obj(
        "Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    x, y, z = d
    assert x == "Lumos"
    assert y == 5
    assert z == ["Makes light"]


def test_typed_namedtuple_asdict(dummy_obj):
    d = dummy_obj(
        "Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    d_dict = d._asdict()
    assert isinstance(d_dict, dict)
    assert d_dict["spell"] == "Lumos"
    assert d_dict["mana"] == 5
    assert d_dict["effect"] == ["Makes light"]


def test_typed_namedtuple_create_from_dict(dummy_obj):
    t = {
        "spell": "Lumos",
        "mana": 5,
        "effect": [
            "Makes light",
        ],
    }
    d = dummy_obj(**t)
    attr_of_obj_test(d)


def test_typed_namedtuple_replace(dummy_obj):
    d = dummy_obj(
        "Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    d = d._replace(mana=10)
    with pytest.raises(AssertionError):
        attr_of_obj_test(d)


def test_typed_namedtuple_default_values():
    Dummy = typed_namedtuple(
        "Dummy", ["spell:str", "mana:int", "effect:list"], defaults=["", 0, []]
    )
    d = Dummy()
    assert d.spell == ""
    assert d.mana == 0
    assert d.effect == []

    # defaults must match fields
    with pytest.raises(TypeError):
        typed_namedtuple("Dummy", ["spell:str", "mana:int", "effect:list"], defaults=[""])

    with pytest.raises(TypeError):
        typed_namedtuple("Dummy", ["spell:str", "mana:int", "effect:list"], defaults=["", 0])


def test_typed_namedtuple_has_nice_docstring(dummy_obj):
    d = dummy_obj(
        "Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    assert d.__doc__ is not None
    assert ":type spell: str" in d.__doc__
    assert ":type mana: int" in d.__doc__
    assert ":type effect: list" in d.__doc__


def test_typed_namedtuple_instantiate_with_incorrect_types_raises_type_error(dummy_obj):
    with pytest.raises(TypeError):
        # spell -> str
        # mana -> int
        # effect -> list
        dummy_obj(mana="Lumos", spell=5, effect="Makes light")


def test_typed_namedtuple_incorrect_default_types_raises_type_error():
    with pytest.raises(TypeError):
        Dummy = typed_namedtuple(
            "Dummy", ["spell:str", "mana:int", "effect:list"], defaults=[0, "", ""]
        )

    with pytest.raises(TypeError):
        Dummy = typed_namedtuple(
            "Dummy",
            ["spell:str", "mana:int or str", "effect:list"],
            defaults=["", (), []],
        )

    with pytest.raises(TypeError):
        Dummy = typed_namedtuple(
            "Dummy",
            ["spell:str", "mana:int or str", "effect:list or tuple"],
            defaults=["", "5", {1, 2}],
        )


def test_typed_namedtuple_incorrect_replace_types_raises_type_error(dummy_obj):
    d = dummy_obj(
        "Lumos",
        mana=5,
        effect=[
            "Makes light",
        ],
    )
    with pytest.raises(TypeError):
        d._replace(effect=b"Makes light")


def test_typed_namedtuple_with_field_names_as_str():
    Dummy = typed_namedtuple("Dummy", "spell:str, mana:int or str,effect:list")
    with pytest.raises(TypeError):
        Dummy(mana="Lumos", spell=5, effect="Makes light")

    with pytest.raises(TypeError):
        Dummy = typed_namedtuple(
            "Dummy", "spell:str, mana:int or str,effect:list", defaults=[0, "", ""]
        )


def test_typed_namedtuple_default_values_and_instantiate_with_some_values():
    Dummy = typed_namedtuple(
        "Dummy", ["spell:str", "mana:int", "effect:list or tuple"], defaults=["", 0, ()]
    )
    d = Dummy("Lumos")

    assert d.spell == "Lumos"
    assert d.mana == 0
    assert d.effect == ()


def test_typed_namedtuple_rename():
    Dummy = typed_namedtuple(
        "Dummy", ["_spell:str", "mana:int", "effect:list or tuple"], rename=True
    )
    d = Dummy("1", 2, [3, 4])
    assert d._0 == "1"

    with pytest.raises(ValueError):
        Dummy = typed_namedtuple("Dummy", ["_spell:str", "mana:int", "effect:list or tuple"])


def test_typed_namedtuple_mixing_typ_and_no_type_not_allowed():
    with pytest.raises(TypeError):
        Dummy = typed_namedtuple("Dummy", ["spell:str", "mana", "effect:list or tuple"])


def test_typed_namedtuple_name_type_as_tuple():
    Dummy = typed_namedtuple(
        "Dummy", [("spell", str), ("mana", int), ("effect", Union[list, tuple])]
    )

    with pytest.raises(TypeError):
        Dummy(
            [
                "Mends torn pieces of paper.",
            ],
            "Papyrus Reparo",
            10,
        )

    with pytest.raises(TypeError):
        Dummy("Papyrus Reparo", 10, {1, 2, 3})


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
