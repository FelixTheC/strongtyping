from functools import partial
from typing import Any

from strongtyping.strong_typing import match_typing


def action(f: Callable[..., Any], frefs: str) -> Any:
    """
    This code is original from Ruud van der Ham https://github.com/salabim/easy_property
    """
    _action: Any = action
    if f.__qualname__ == _action.qualname:
        if any(_action.f[fref] is not None for fref in frefs.split("_")):
            raise AttributeError("decorator defined twice")
    else:
        _action.f.update({}.fromkeys(_action.f, None))  # reset all values to None
        _action.qualname = f.__qualname__
    _action.f.update({}.fromkeys(frefs.split("_"), f))  # set all frefs values to f

    # this line was added by myself
    _action.f["setter"] = (
        match_typing(_action.f["setter"]) if _action.f["setter"] is not None else None
    )

    return property(
        *(
            _action.f[ref] if (ref != "documenter" or _action.f[ref] is None) else _action.f[ref](0)
            for ref in _action.f
        )
    )


_action_obj: Any = action
_action_obj.qualname = None
_action_obj.f = dict.fromkeys(["getter", "setter", "deleter", "documenter"], None)

globals().update(
    {fref: partial(action, frefs=fref) for fref in {**_action_obj.f, "getter_setter": None}}
)
