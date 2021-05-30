#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type as TypingType, Union

from mypy.errorcodes import ErrorCode
from mypy.nodes import (
    ARG_NAMED,
    ARG_NAMED_OPT,
    ARG_OPT,
    ARG_POS,
    ARG_STAR2,
    MDEF,
    Argument,
    AssignmentStmt,
    Block,
    CallExpr,
    ClassDef,
    Context,
    Decorator,
    EllipsisExpr,
    FuncBase,
    FuncDef,
    JsonDict,
    MemberExpr,
    NameExpr,
    PassStmt,
    PlaceholderNode,
    RefExpr,
    StrExpr,
    SymbolNode,
    SymbolTableNode,
    TempNode,
    TypeInfo,
    TypeVarExpr,
    Var,
)
from mypy.options import Options
from mypy.plugin import (
    AnalyzeTypeContext,
    AttributeContext,
    CheckerPluginInterface,
    ClassDefContext,
    DynamicClassDefContext,
    FunctionContext,
    FunctionSigContext,
    MethodContext,
    MethodSigContext,
    Plugin,
    SemanticAnalyzerPluginInterface,
)
from mypy.plugins import dataclasses
from mypy.semanal import set_callable_name  # type: ignore
from mypy.server.trigger import make_wildcard_trigger
from mypy.types import (
    AnyType,
    CallableType,
    Instance,
    NoneTyp,
    NoneType,
    ProperType,
    Type,
    TypeOfAny,
    TypeType,
    TypeVar,
    TypeVarDef,
    TypeVarType,
    UnionType,
    get_proper_type,
)
from mypy.typevars import fill_typevars
from mypy.util import get_unique_redefinition_name

T = TypeVar("T")

VALIDATOR_TYPE = "strongtyping.strong_typing_utils.Validator"  # type: Final


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
    assert len(ctx.type.args) == 2
    new_arg = AnyType(TypeOfAny.special_form)
    return Instance(
        ctx.type,  # <- muste be a mypy.nodes.TypeInfo
        [UnionType([new_arg, new_arg])],
        line=ctx.context.line,
        column=ctx.context.column,
    )


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
