import typing

from strongtyping.strong_typing_utils import py_version as py_version
from typing import Any

Validator: Any
IterValidator: Any


class FinalType:
    def __init__(self, attr: typing.Type):
        pass

    @classmethod
    def cast(cls, origin: Any, new: typing.Type):
        pass
