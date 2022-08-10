from numbers import Complex, Real
from typing import Optional, Union

import pytest


@pytest.mark.xfail
def test_entity_fails():
    from strongtyping.types import Constant, Entity

    class X(Entity):
        x: Constant[dict[int, str]]
        y: Constant[Optional[Union[float, int]]]
        z: Constant[Union[Real, str]]

    class Y(X):
        x: Constant[dict[int, str]]
        y: Constant[int]
        z: Constant[Union[Complex, str]]


def test_entity():
    from strongtyping.types import Constant, Entity

    class X(Entity):
        x: Constant[dict[int, str]]
        y: Constant[Optional[Union[float, int]]]
        z: Constant[list[str]]

    class Y(X):
        x: Constant[dict[int, str]]
        y: Constant[int]
        z: Constant[list[Optional[str]]]
