from enum import IntEnum
from os import environ


class SeverityLevel(IntEnum):
    DISABLED = 0
    ENABLED = 1
    WARNING = 2

    @property
    def value_as_str(self) -> str:
        return str(self.value)


def set_severity_level(_level: SeverityLevel) -> None:
    environ["ST_SEVERITY"] = _level.value_as_str


def set_dry_run(val: bool, /) -> None:
    if val:
        environ["ST_SEVERITY"] = SeverityLevel.WARNING.value_as_str
    else:
        environ["ST_SEVERITY"] = SeverityLevel.ENABLED.value_as_str
