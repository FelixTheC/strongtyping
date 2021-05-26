from enum import Enum
from typing import Any

class SEVERITY_LEVEL(Enum):
    DISABLED: int = ...
    ENABLED: int = ...
    WARNING: int = ...
    @property
    def value_as_str(self): ...

def set_severity_level(_level: SEVERITY_LEVEL) -> Any: ...