from configparser import ConfigParser as ConfigParser
from typing import Any, Callable, Optional, Type as TypingType, Union

from mypy.nodes import (
    ARG_OPT as ARG_OPT,
    ARG_POS as ARG_POS,
    ARG_STAR2 as ARG_STAR2,
    MDEF as MDEF,
    Argument,
    AssignmentStmt as AssignmentStmt,
    Block as Block,
    CallExpr as CallExpr,
    ClassDef as ClassDef,
    Context as Context,
    Decorator as Decorator,
    EllipsisExpr as EllipsisExpr,
    FuncBase as FuncBase,
    FuncDef as FuncDef,
    JsonDict as JsonDict,
    MemberExpr as MemberExpr,
    NameExpr as NameExpr,
    PassStmt as PassStmt,
    PlaceholderNode as PlaceholderNode,
    RefExpr as RefExpr,
    StrExpr as StrExpr,
    SymbolNode as SymbolNode,
    SymbolTableNode as SymbolTableNode,
    TempNode as TempNode,
    TypeInfo as TypeInfo,
    TypeVarExpr as TypeVarExpr,
    Var,
)
from mypy.options import Options as Options
from mypy.plugin import (
    AnalyzeTypeContext as AnalyzeTypeContext,
    AttributeContext as AttributeContext,
    CheckerPluginInterface as CheckerPluginInterface,
    ClassDefContext as ClassDefContext,
    DynamicClassDefContext as DynamicClassDefContext,
    FunctionContext as FunctionContext,
    FunctionSigContext as FunctionSigContext,
    MethodContext as MethodContext,
    MethodSigContext as MethodSigContext,
    Plugin,
    SemanticAnalyzerPluginInterface as SemanticAnalyzerPluginInterface,
)
from mypy.plugins import dataclasses as dataclasses
from mypy.semanal import set_callable_name as set_callable_name
from mypy.server.trigger import make_wildcard_trigger as make_wildcard_trigger
from mypy.types import (
    CallableType as CallableType,
    Instance as Instance,
    NoneTyp as NoneTyp,
    NoneType as NoneType,
    ProperType as ProperType,
    Type as Type,
    TypeType as TypeType,
    TypeVar,
    TypeVarDef as TypeVarDef,
    TypeVarType as TypeVarType,
    UnionType as UnionType,
    get_proper_type as get_proper_type,
)
from mypy.typevars import fill_typevars as fill_typevars
from mypy.util import get_unique_redefinition_name as get_unique_redefinition_name

T = TypeVar('T')
VALIDATOR_TYPE: Final

def plugin(version: str) -> TypingType[Plugin]: ...

class StrongtypingPlugin(Plugin):
    def __init__(self, options: Options) -> None: ...
    def get_type_analyze_hook(self, fullname: str) -> Optional[Callable[[AnalyzeTypeContext], Type]]: ...

def validator_callback(ctx: AnalyzeTypeContext) -> Type: ...

ERROR_UNEXPECTED: Any

def error_invalid_config_value(name: str, api: SemanticAnalyzerPluginInterface, context: Context) -> None: ...
def get_fullname(x: Union[FuncBase, SymbolNode]) -> str: ...
def get_name(x: Union[FuncBase, SymbolNode]) -> str: ...

class ValidatorType:
    name: Any = ...
    is_required: Any = ...
    alias: Any = ...
    has_dynamic_alias: Any = ...
    line: Any = ...
    column: Any = ...
    def __init__(self, name: str, is_required: bool, alias: Optional[str], has_dynamic_alias: bool, line: int, column: int) -> None: ...
    def to_var(self, info: TypeInfo, use_alias: bool) -> Var: ...
    def to_argument(self, info: TypeInfo, typed: bool, force_optional: bool, use_alias: bool) -> Argument: ...
    def serialize(self) -> JsonDict: ...
    @classmethod
    def deserialize(cls: Any, info: TypeInfo, data: JsonDict) -> ValidatorType: ...
