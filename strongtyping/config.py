#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 20.07.20
@author: felix
"""

from enum import Enum
from os import environ


class SEVERITY_LEVEL(Enum):
    DISABLED = 0
    ENABLED = 1
    WARNING = 2

    @property
    def value_as_str(self) -> str:
        return str(self.value)


def set_severity_level(_level: SEVERITY_LEVEL) -> None:
    environ["ST_SEVERITY"] = _level.value_as_str


def set_dry_run(val: bool, /) -> None:
    if val:
        environ["ST_SEVERITY"] = SEVERITY_LEVEL.WARNING.value_as_str
    else:
        environ["ST_SEVERITY"] = SEVERITY_LEVEL.ENABLED.value_as_str
