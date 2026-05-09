#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import Any


class TypeMismatch(AttributeError):
    def __init__(
        self,
        message: str,
        failed_params: Any = None,
        param_values: Any = None,
        annotations: Any = None,
    ) -> None:
        super().__init__()
        print(message, file=sys.stderr)


class ValidationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__()
        print(message, file=sys.stderr)


class UndefinedKey(Exception):
    def __init__(self, message: str) -> None:
        super().__init__()
        print(message, file=sys.stderr)
