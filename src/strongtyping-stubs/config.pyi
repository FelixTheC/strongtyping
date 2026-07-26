from enum import Enum

class SEVERITY_LEVEL(Enum):
    DISABLED = 0
    ENABLED = 1
    WARNING = 2
    @property
    def value_as_str(self) -> str: ...

def set_severity_level(_level: SEVERITY_LEVEL) -> None: ...
def set_dry_run(val: bool, /) -> None: ...
