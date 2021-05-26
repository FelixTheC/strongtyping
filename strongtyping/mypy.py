#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from typing import Type as TypingType
from typing import Union

from mypy.errorcodes import ErrorCode
from mypy.nodes import (ARG_NAMED, ARG_NAMED_OPT, ARG_OPT, ARG_POS, ARG_STAR2,
                        MDEF, Argument, AssignmentStmt, Block, CallExpr,
                        ClassDef, Context, Decorator, EllipsisExpr, FuncBase,
                        FuncDef, JsonDict, MemberExpr, NameExpr, PassStmt,
                        PlaceholderNode, RefExpr, StrExpr, SymbolNode,
                        SymbolTableNode, TempNode, TypeInfo, TypeVarExpr, Var)
from mypy.options import Options
from mypy.plugin import (CheckerPluginInterface, ClassDefContext,
                         MethodContext, Plugin,
                         SemanticAnalyzerPluginInterface)
from mypy.plugins import dataclasses
from mypy.semanal import set_callable_name  # type: ignore
from mypy.server.trigger import make_wildcard_trigger
from mypy.types import (AnyType, CallableType, Instance, NoneType, Type,
                        TypeOfAny, TypeType, TypeVarDef, TypeVarType,
                        UnionType, get_proper_type)
from mypy.typevars import fill_typevars
from mypy.util import get_unique_redefinition_name

CONFIGFILE_KEY = 'strongtyping-mypy'
DECORATOR_FULLNAME = 'strongtyping.strong_typing.match_typing'
CLASS_DECORATOR_FULLNAME = 'strongtyping.strong_typing.match_class_typing'


def plugin(version: str) -> 'TypingType[Plugin]':
    """
    `version` is the mypy version string
    We might want to use this to print a warning if the mypy version being used is
    newer, or especially older, than we expect (or need).
    """
    return StrongtypingPlugin


class StrongtypingPlugin(Plugin):
    def __init__(self, options: Options) -> None:
        with open('test.txt', 'w') as file:
            print(vars(self), file=file)
        super().__init__(options)

    # def get_base_class_hook(self, fullname: str) -> 'Optional[Callable[[ClassDefContext], None]]':
    #     sym = self.lookup_fully_qualified(fullname)
    #     if sym and isinstance(sym.node, TypeInfo):  # pragma: no branch
    #         for base in sym.node.mro:
    #             print(f'{base = }')
    #         # No branching may occur if the mypy cache has not been cleared
    #         # if any(get_fullname(base) == BASEMODEL_FULLNAME for base in sym.node.mro):
    #         #     return self._pydantic_model_class_maker_callback
    #     return None

    def get_type_analyze_hook(self, fullname: str) -> Optional[Any]:
        if fullname.startswith('strongtyping') or fullname.startswith('strongtyping.strong_typing'):
            print(f'{fullname = }')
            return self._ctx.default_return_type
        return None

    def get_function_hook(self, fullname: str) -> Optional[Callable[[MethodContext], None]]:
        if fullname.startswith('strongtyping') or fullname.startswith('strongtyping.strong_typing'):
            raise RuntimeError(f'{fullname = }')
        return None

    def get_method_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname.startswith('strongtyping') or fullname.startswith('strongtyping.strong_typing'):
            raise RuntimeError(f'{fullname = }')
        return None

    def get_class_decorator_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname.startswith('strongtyping') or fullname.startswith('strongtyping.strong_typing'):
            raise RuntimeError(f'{fullname = }')
        return None

    # def _pydantic_model_class_maker_callback(self, ctx: ClassDefContext) -> None:
    #     transformer = PydanticModelTransformer(ctx, self.plugin_config)
    #     transformer.transform()


class StrongtypingPluginConfig:
    __slots__ = ('init_forbid_extra', 'init_typed',
                 'warn_required_dynamic_aliases', 'warn_untyped_fields')
    init_forbid_extra: bool
    init_typed: bool
    warn_required_dynamic_aliases: bool
    warn_untyped_fields: bool

    def __init__(self, options: Options) -> None:
        if options.config_file is None:  # pragma: no cover
            return
        plugin_config = ConfigParser()
        plugin_config.read(options.config_file)
        for key in self.__slots__:
            setting = plugin_config.getboolean(CONFIGFILE_KEY, key, fallback=False)
            setattr(self, key, setting)


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
