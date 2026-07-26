import inspect
import pprint
import re
import textwrap
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type

from strongtyping.strong_typing_utils import get_origins, get_possible_types

Pattern = re.compile(r"(\$\d[a-zA-Z0-9, ()\n]+)")


def getsource(object: Any) -> str:
    """Return the text of the source code for an object.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a single string.  An
    OSError is raised if the source code cannot be retrieved."""
    lines, lnum = inspect.getsourcelines(object)
    return "".join(lines[1:])


# def numpy_doc_string():
#     """
#     Some short description
#
#     Parameters
#     ----------
#     val_a : int
#         some infos if available
#     val_b : {int, float}, optional
#         default is 'value'
#
#     Returns
#     -------
#     string
#         some info if available
#
#     Raises
#     ------
#     TypeMisMatch
#         if the passed values not matching the required ones
#     """
#
#
# def rest_doc_string(val_a: int, val_b: int = 10) -> int:
#     """
#     Some short description
#
#     :param val_a: some info
#     :param val_b: (Default value = '10')
#     :type val_a: int
#     :returns: int
#     """


ARGUMENT_TYPE = {
    inspect.Parameter.KEYWORD_ONLY: "keyword only argument",
    inspect.Parameter.POSITIONAL_ONLY: "postional only argument",
    inspect.Parameter.POSITIONAL_OR_KEYWORD: "argument",
    inspect.Parameter.VAR_POSITIONAL: "variadic arguments",
    inspect.Parameter.VAR_KEYWORD: "variadic keyword arguments",
}


def union_types(val: Any, type_origins: Any) -> str:
    types: list[str] = []
    possible = get_possible_types(type_origins)
    if possible is None:
        return str(type_origins)
    for type_origin in possible:
        try:
            types.append(type_origin.__name__)
        except AttributeError:
            types.append(get_type_info(val, type_origin))
    return " or ".join(types)


def get_type_info(val: Any, type_origins: Any) -> str:
    origins = get_origins(type_origins)
    val_origins = get_origins(val)
    if get_origins(val)[1] == "Union":
        try:
            return " or ".join([type_origin.__name__ for type_origin in type_origins])
        except AttributeError:
            return get_type_info(val, type_origins)
        except TypeError:
            return union_types(val, type_origins)
    elif origins[1] == "Union":
        return union_types(val, type_origins)
    elif origins[1].lower() == "dict":
        try:
            return f"{get_origins(val)[1]}({get_type_info(val, type_origins[0])}, {get_type_info(val, type_origins[1])})"
        except TypeError:
            pos_types = get_possible_types(type_origins)
            if pos_types:
                text = ", ".join([get_type_info(val, type_origin) for type_origin in pos_types])
                return f"{get_origins(val)[1]}({text})"
            return ""
    elif origins[1].lower() in ("list", "tuple", "set"):
        pos_types = get_possible_types(type_origins)
        if pos_types:
            text = ", ".join([get_type_info(val, type_origin) for type_origin in pos_types])
            if origins[1] != "None" and get_origins(val)[1] != origins[1]:
                return f"{origins[1]}({text})"
            return f"{get_origins(val)[1]}({text})"
        return ""
    elif val_origins[1] == "Literal":
        text = " or ".join([f"`{elem}`" for elem in type_origins])
        return f"`{type(type_origins[0]).__name__}` allowed values are {text}"
    elif val_origins[1] == "TypedDict" or val_origins[1] == "_TypedDictMeta":
        required = " required" if val_origins[0].__total__ else ""
        fields = {
            key: get_type_info(key, val) for key, val in val_origins[0].__annotations__.items()
        }
        return f"{val.__name__}[TypedDict]{required} fields are \n\t`{pprint.pformat(fields, sort_dicts=False)}`"
    elif "Validator" in origins[1]:
        required_type, *not_needed = type_origins.__args__
        text = f"{get_type_info(val, required_type)}[{origins[1]}]"
        return text
    elif val_origins[1] == "args":
        return "tuple"
    elif val_origins[1] == "kwargs":
        return "dict"
    else:
        if type_origins:
            try:
                origins_str = ", ".join((type_origin.__name__ for type_origin in type_origins))
            except AttributeError:
                if len(type_origins) == 1:
                    return f"{get_origins(val)[1]}({get_type_info(val, type_origins[0])})"
                else:
                    return (
                        f"{get_origins(val)[1]}({get_type_info(val, type_origins[0])},"
                        f" {get_type_info(val, type_origins[1])})"
                    )
            except TypeError:
                try:
                    return str(type_origins.__name__)
                except AttributeError:
                    return str(type_origins)
            else:
                return f"{get_origins(val)[1]}({origins_str})"
        else:
            if hasattr(val, "__name__"):
                return str(val.__name__)
            return str(val)


def docs_from_typing_numpy_format(
    annotations: Dict[str, Any],
    additional_infos: Dict[str, str],
    func_params: Dict[str, inspect.Parameter],
    remove_linebreak: bool,
    func_info: str,
) -> tuple[str, str]:
    doc_infos = ["Parameters", "----------"]
    type_infos = ["Returns", "-------"]
    func_param_keys = [
        key for key in func_params.keys() if key != "self" and key not in annotations
    ]
    annotation_keys = list(annotations.keys())

    for idx, key in enumerate((annotation_keys + func_param_keys), 1):
        if key != "return":
            val = annotations.get(key, func_params[key])
            type_origins = get_possible_types(val)
            predefined_info = "\n\t".join(additional_infos.get(f"${idx}", "").split("\n"))
            predefined_info = f"\n\t{predefined_info}" if predefined_info else ""

            info_str = f"{key} : {ARGUMENT_TYPE[func_params[key].kind]} of type {get_type_info(val, type_origins)}"

            if func_params[key].default is not inspect._empty:
                info_str = f"{info_str}\n\tDefault is {func_params[key].default}"

            info_str = f"{info_str}{predefined_info}"
            doc_infos.append(info_str)
    if "return" in annotations:
        doc_infos.append("")
        type_infos.append(get_type_info(annotations["return"], annotations["return"]))
    else:
        type_infos = []

    lb = "" if remove_linebreak else "\n"
    return lb + "\n".join(doc_infos + type_infos), func_info


def docs_from_typing_reST_format(
    annotations: Dict[str, Any],
    additional_infos: Dict[str, str],
    func_params: Dict[str, inspect.Parameter],
    remove_linebreak: bool,
    func_info: str,
) -> tuple[str, str]:
    doc_infos = []
    type_infos = []
    func_param_keys = [
        key for key in func_params.keys() if key != "self" and key not in annotations
    ]
    annotation_keys = list(annotations.keys())
    for idx, key in enumerate((annotation_keys + func_param_keys), 1):
        if key != "return":
            val = annotations.get(key, func_params[key])
            type_origins = get_possible_types(val)
            predefined_info = "\n\t".join(additional_infos.get(f"${idx}", "").split("\n"))
            predefined_info = f"\n\t{predefined_info}" if predefined_info else ""
            info_str = f":param {key}: {ARGUMENT_TYPE[func_params[key].kind]} {predefined_info}"

            if func_params[key].default is not inspect._empty:
                info_str = f"{info_str} (Default value = {func_params[key].default})"

            doc_infos.append(info_str)

            type_infos.append(f":type {key}: {get_type_info(val, type_origins)}")

    if "return" in annotations:
        type_infos.append(
            f":returns: {get_type_info(annotations['return'], annotations['return'])}"
        )

    lb = "" if remove_linebreak else "\n"
    return lb + "\n".join(doc_infos + type_infos), func_info


def docs_from_typing(func: Callable[..., Any], remove_linebreak: bool, style: str) -> Any:
    annotations: Dict[str, Any] = func.__annotations__
    func_params: Dict[str, inspect.Parameter] = dict(inspect.signature(func).parameters)
    if func.__doc__:
        if not func.__doc__.endswith("\n") and func.__doc__ != "":
            func_doc = f"{func.__doc__}\n"
        else:
            func_doc = func.__doc__
        additional_infos_list = Pattern.split(textwrap.dedent(func_doc))
        func_info = textwrap.dedent(additional_infos_list[0])
        _additional_infos_gen: Any = [
            tuple(filter(lambda x: len(x) > 1, map(str.strip, re.split(r"(\$\d)", info))))
            for info in additional_infos_list
            if info and info[0] == "$"
        ]
        additional_infos: Dict[str, str] = dict(_additional_infos_gen)
    else:
        if func.__name__ != "__init__":
            func_info = f"Function {func.__name__}\n\n"
        else:
            func_info = "\n"
        additional_infos = {}
    if style == "rest":
        return docs_from_typing_reST_format(
            annotations, additional_infos, func_params, remove_linebreak, func_info
        )
    elif style == "numpy":
        return docs_from_typing_numpy_format(
            annotations, additional_infos, func_params, remove_linebreak, func_info
        )


def rest_docs_from_typing(
    _func: Optional[Callable[..., Any]] = None,
    *,
    insert_at: Optional[str] = None,
    remove_linebreak: bool = False,
) -> Any:
    def wrapper(func: Callable[..., Any]) -> Any:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        text, func_doc = docs_from_typing(func, remove_linebreak, style="rest")

        _inner: Any = inner
        if insert_at is not None:
            _inner.__doc__ = func_doc.replace(insert_at, text)
        else:
            _inner.__doc__ = f"{func_doc}{text}"
        _inner.has_auto_generated_docs = True
        return _inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper


def numpy_docs_from_typing(
    _func: Optional[Callable[..., Any]] = None,
    *,
    insert_at: Optional[str] = None,
    remove_linebreak: bool = False,
) -> Any:
    def wrapper(func: Callable[..., Any]) -> Any:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        text, func_doc = docs_from_typing(func, remove_linebreak, style="numpy")

        _inner: Any = inner
        if insert_at is not None:
            _inner.__doc__ = func_doc.replace(insert_at, text)
        else:
            _inner.__doc__ = f"{func_doc}{text}"
        _inner.has_auto_generated_docs = True
        return _inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper


def class_docs_from_typing(_cls: Optional[Type[Any]] = None, *, doc_type: str = "reST") -> Any:
    def wrapper(cls: Type[Any]) -> Any:
        docs_formatter: Any = (
            rest_docs_from_typing if doc_type.lower() == "rest" else numpy_docs_from_typing
        )
        cls.__doc__ = f"{cls.__doc__}{docs_formatter(cls.__init__).__doc__}"
        cls.__init__.__doc__ = ""
        users_funcs = [
            func
            for func in dir(cls)
            if inspect.isfunction(getattr(cls, func)) and func != "__init__"
        ]
        for func in users_funcs:
            cls_method: Any = getattr(cls, func)
            if cls_method.__annotations__ and not hasattr(cls_method, "has_auto_generated_docs"):
                cls_method.__doc__ = docs_formatter(getattr(cls, func)).__doc__
        return cls

    if _cls is not None:
        return wrapper(_cls)
    else:
        return wrapper
