from typing import Any

from strongtyping.config import SEVERITY_LEVEL as SEVERITY_LEVEL

logger: Any

def remove_subclass(args: Any, subclass: Any): ...

SEVERITY_CONFIG: Any
exclude_builtins: Any

def install_st_m() -> None: ...
def action(f: Any, frefs: Any, type_function: Any): ...


def ORIGINAL_DUCK_TYPES():
    return None