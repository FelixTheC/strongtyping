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
    def value_as_str(self):
        return str(self.value)


def set_severity_level(_level: SEVERITY_LEVEL):
    environ["ST_SEVERITY"] = _level.value_as_str
