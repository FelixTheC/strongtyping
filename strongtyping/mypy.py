#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Callable, Optional, Type as TypingType, Union

from mypy.errorcodes import ErrorCode
from mypy.nodes import FuncBase, SymbolNode
from mypy.options import Options
from mypy.plugin import AnalyzeTypeContext, Plugin
from mypy.semanal import set_callable_name  # type: ignore
from mypy.types import Type, TypeVar

T = TypeVar("T")

VALIDATOR_TYPE = "strongtyping.strong_typing_utils.Validator"  # type: Final
ERROR_UNEXPECTED = ErrorCode("strongtyping-unexpected", "Unexpected behavior", "strongtyping")


def plugin(version: str) -> "TypingType[Plugin]":
    """
    `version` is the mypy version string
    We might want to use this to print a warning if the mypy version being used is
    newer, or especially older, than we expect (or need).
    """
    return StrongtypingPlugin


class StrongtypingPlugin(Plugin):
    def __init__(self, options: Options) -> None:
        super().__init__(options)

    def get_type_analyze_hook(
        self, fullname: str
    ) -> Optional[Callable[[AnalyzeTypeContext], Type]]:
        if fullname == VALIDATOR_TYPE:
            return validator_callback
        return None


def validator_callback(ctx: AnalyzeTypeContext) -> Type:
    typ, _, api = ctx
    name = typ.name.split(".")[-1]
    return api.named_type("strongtyping.types." + name)


def get_fullname(x: Union[FuncBase, SymbolNode]) -> str:
    """
    Used for compatibility with mypy 0.740; can be dropped once support for 0.740 is dropped.
    """
    fn = x.fullname
    if callable(fn):  # pragma: no cover
        return fn()
    return fn


def get_name(x: Union[FuncBase, SymbolNode]) -> str:
    """
    Used for compatibility with mypy 0.740; can be dropped once support for 0.740 is dropped.
    """
    fn = x.name
    if callable(fn):  # pragma: no cover
        return fn()
    return fn
