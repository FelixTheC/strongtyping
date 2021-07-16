from typing import Any, Type

from strongtyping.strong_typing_utils import py_version as py_version

Validator: Any
IterValidator: Any

class FrozenType:
    def __init__(self, *args):
        pass
    @classmethod
    def cast(cls, instance: Any, origin: Any, new: Type):
        pass
