from numbers import Integral, Real
from typing import Container, MutableMapping

import pytest

UNIMPORTED = object()

try:
    from requests.structures import CaseInsensitiveDict
except ImportError:
    CaseInsensitiveDict = UNIMPORTED

from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import TypeMismatch


def test_int_float_duck_typing():
    @match_typing(allow_duck_typing=True)
    def adder(x: int, y: float):
        return x + y

    assert adder(2, 2.5) == 4.5
    assert adder(2, 5) == 7

    with pytest.raises(TypeMismatch):
        adder(2.5, 5)


def test_complex_duck_typing():
    @match_typing(allow_duck_typing=True)
    def adder(x: float, y: complex):
        return x + y

    assert adder(2.5, 2.5) == 5
    assert adder(3.5, 1.5) == 5


def test_integral_real_duck_typing():
    @match_typing(allow_duck_typing=True)
    def adder(x: Integral, y: Real):
        return x + y

    assert adder(2, 2.5) == 4.5
    assert adder(2, 5) == 7

    with pytest.raises(TypeMismatch):
        adder(2.5, 5)


def test_bytearray_duck_typing():
    @match_typing(allow_duck_typing=True)
    def adder(x: bytearray, y: bytes):
        return x + y

    assert adder(bytearray([1, 2, 3]), bytes([1, 2, 3])) == bytearray(b"\x01\x02\x03\x01\x02\x03")
    assert adder(bytearray([1, 2, 3]), bytearray([1, 2, 3])) == bytearray(
        b"\x01\x02\x03\x01\x02\x03"
    )

    with pytest.raises(TypeMismatch):
        adder(bytes([1, 2, 3]), bytearray([1, 2, 3]))


@pytest.mark.skipif(CaseInsensitiveDict is UNIMPORTED, reason="CaseInsensitiveDict is required")
def test_mro_compatibility_duck_typing():
    @match_typing(allow_duck_typing=True)
    def dummy(x: MutableMapping):
        return x

    assert dummy(CaseInsensitiveDict()) is not None

    class CustomContainer(Container):
        def __init__(self):
            pass

        def __contains__(self, item):
            return True

    @match_typing(allow_duck_typing=True)
    def dummy_2(x: Container):
        return x

    assert dummy_2(CustomContainer()) is not None


if __name__ == "__main__":
    pytest.main(["-vv", "-s", __file__])
