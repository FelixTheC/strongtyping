from enum import IntEnum

class SeverityLevel(IntEnum):
    DISABLED = 0
    ENABLED = 1
    WARNING = 2
    @property
    def value_as_str(self) -> str: ...

def set_severity_level(_level: SeverityLevel) -> None: ...
def set_dry_run(val: bool, /) -> None: ...
