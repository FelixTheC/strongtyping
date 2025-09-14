from typing import TypedDict

from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import TypeMismatch, ValidationError


def validate_typed_dict(base: TypedDict, /, data: dict) -> bool:
    # noinspection PyTypeHints
    @match_typing
    def inner(obj: base):
        pass

    try:
        inner(data)
    except (TypeMismatch, ValidationError):
        return False
    return True
