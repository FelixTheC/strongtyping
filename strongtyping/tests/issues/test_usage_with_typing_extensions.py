import pytest

from strongtyping.strong_typing import match_class_typing
from typing_extensions import NotRequired, Required, TypedDict

from strongtyping.strong_typing_utils import TypeMisMatch


def test_nested_typed_dicts():
    @match_class_typing
    class ChildType(TypedDict):
        key_a: int
        key_b: int


    @match_class_typing
    class ParentType(TypedDict):
        child: ChildType
        not_required: NotRequired[int]

    parent = {"child": {"key_a": 1, "key_b": 2}}
    ParentType(parent)


def test_not_required():

    @match_class_typing
    class ChildType(TypedDict):
        key_a: int
        key_b: int


    @match_class_typing
    class ParentType(TypedDict):
        child: ChildType
        not_required: NotRequired[int]

    parent = {"not_required": 3, "child": {"key_a": 1, "key_b": 2}}
    ParentType(parent)


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

    with pytest.raises(TypeMisMatch):
            Regisseur(name="Alfonso Cuarón", movie=Movie, year=2004)

    with pytest.raises(TypeMisMatch):
        Regisseur(name="Alfonso Cuarón", year=2004)


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
