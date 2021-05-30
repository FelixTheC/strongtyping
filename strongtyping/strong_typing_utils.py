#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 19.11.20
@author: felix
"""
import inspect
import json
import os
import sys
import typing
from functools import lru_cache, partial
from queue import Queue
from typing import Any, TypeVar, _GenericAlias, _SpecialForm, _type_repr  # type: ignore

from strongtyping._utils import install_st_m

install_st_m()

try:
    from strongtyping_modules.strongtyping_modules import dict_elements  # type: ignore
    from strongtyping_modules.strongtyping_modules import list_elements  # type: ignore
    from strongtyping_modules.strongtyping_modules import set_elements  # type: ignore
    from strongtyping_modules.strongtyping_modules import tuple_elements  # type: ignore
except ImportError as e:
    extension_module: bool = False
else:
    extension_module = bool(int(os.environ["ST_MODULES_INSTALLED"]))


empty = object()
default_return_queue = Queue()


class TypeMisMatch(AttributeError):
    def __init__(self, message):
        super().__init__()
        print(message)


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        print(message)


py_version = sys.version_info.minor
if hasattr(typing, "_GenericAlias"):
    typing_base_class = typing._GenericAlias  # type: ignore
else:
    typing_base_class = typing.GenericMeta  # type: ignore


@lru_cache(maxsize=1024)
def get_possible_types(typ_to_check) -> typing.Union[tuple, None]:
    """
    :param typ_to_check: some typing like List[str], Dict[str, int], Tuple[Union[str, int], List[int]]
    :return: the inner types, classes of the type
        - List[str] = (str, )
        - Dict[str, int] = (str, int, )
        - Tuple[Union[str, int], List[int]] = (Union[str, int], List[int], )
    """
    if extension_module:
        if not hasattr(typ_to_check, "__args__"):
            try:
                return typ_to_check.__origin__
            except AttributeError:
                return None
    if hasattr(typ_to_check, "__args__") and typ_to_check.__args__ is not None:
        return tuple(typ for typ in typ_to_check.__args__ if not isinstance(typ, TypeVar))
    else:
        return None


def get_origins(typ_to_check: Any) -> tuple:
    """
    :param typ_to_check: typ_to_check: some typing like List[str], Dict[str, int], Tuple[Union[str, int], List[int]]
    :return: the class, alias_class and the class name
        - List[str] = (list, 'List')
        - Dict[str, int] = (dict, 'Dict')
        - Tuple[Union[str, int], List[int]] = (tuple, 'Tuple)
        - FunctionType = (None, 'None')
    """
    origin = None
    if hasattr(typ_to_check, "__origin__") or hasattr(typ_to_check, "__orig_bases__"):
        if py_version >= 3.9 and hasattr(typ_to_check.__origin__, "__name__"):
            origin = typ_to_check.__origin__.__name__
        else:
            if typ_to_check.__origin__ is not None:
                origin = typ_to_check.__origin__
            else:
                origin = typ_to_check.__orig_bases__

    if hasattr(origin, "_name"):
        origin_name = origin._name  # type: ignore
    else:
        if hasattr(typ_to_check, "_name"):
            origin_name = typ_to_check._name
        else:
            origin_name = str(origin).replace("typing.", "")
    return origin, origin_name


def checking_typing_dict(arg: Any, possible_types: tuple, *args):
    if not isinstance(arg, dict):
        return False
    if isinstance(arg, dict) and not possible_types:
        return True
    try:
        key, val = possible_types
    except (ValueError, TypeError):
        return isinstance(arg, dict)
    else:
        try:
            result_key = all(check_type(a, key) for a in arg.keys())
        except AttributeError:
            result_key = all(isinstance(k, key) for k in arg.keys())
        try:
            result_val = all(check_type(a, val) for a in arg.values())
        except AttributeError:
            result_val = all(isinstance(v, val) for v in arg.values())
        return result_key and result_val


def checking_typing_set(arg: Any, possible_types: tuple, *args, **kwargs):
    if not possible_types:
        return isinstance(arg, set)
    possible_type = possible_types[0]
    return isinstance(arg, set) and all(
        check_type(argument, possible_type, **kwargs) for argument in arg
    )


def checking_typing_type(arg: Any, possible_types: tuple, *args, **kwargs):
    try:
        arguments = arg.__mro__
    except AttributeError:
        return any(
            check_type(arg, possible_type, mro=False, **kwargs) for possible_type in possible_types
        )
    else:
        return any(
            check_type(arguments, possible_type, mro=True, **kwargs)
            for possible_type in possible_types
        )


def checking_typing_union(arg: Any, possible_types: tuple, mro, **kwargs):
    if mro:
        return any(pssble_type in arg for pssble_type in possible_types)
    try:
        is_instance = isinstance(arg, possible_types)
    except TypeError:
        return any(check_type(arg, typ, **kwargs) for typ in possible_types)
    else:
        if not is_instance:
            return False
        else:
            return validate_object(arg, kwargs.get("validation_with"))


def checking_typing_iterator(arg: Any, *args, **kwargs):
    return hasattr(arg, "__iter__") and hasattr(arg, "__next__")


def checking_typing_callable(arg: Any, possible_types: tuple, *args, **kwargs):
    insp = inspect.signature(arg)
    return_val = insp.return_annotation == possible_types[-1]
    params = insp.parameters
    return return_val and all(p.annotation == pt for p, pt in zip(params.values(), possible_types))


def checking_typing_tuple(arg: Any, possible_types: tuple, *args, **kwargs):
    if not possible_types:
        return isinstance(arg, tuple)
    if Ellipsis in possible_types and isinstance(arg, tuple):
        if not arg:
            return True
        return checking_ellipsis(arg, possible_types, **kwargs)
    if not isinstance(arg, tuple) or not (len(arg) == len(possible_types)):
        return False
    return all(check_type(argument, typ, **kwargs) for argument, typ in zip(arg, possible_types))


def checking_typing_list(arg: Any, possible_types: tuple, *args, **kwargs):
    if not isinstance(arg, list):
        return False
    if isinstance(arg, list) and not possible_types:
        return True
    possible_type = possible_types[0]
    return all(check_type(argument, possible_type, **kwargs) for argument in arg)


def checking_ellipsis(arg, possible_types, *args, **kwargs):
    possible_types = [pt for pt in possible_types if pt is not Ellipsis]
    possible_type = possible_types[0]
    return all(check_type(argument, possible_type, **kwargs) for argument in arg)


def checking_typing_json(arg, possible_types, *args, **kwargs):
    try:
        possible_types.dumps(arg)
    except TypeError:
        return isinstance(arg, str)
    else:
        return True


def checking_typing_generator(arg, possible_types, *args, **kwargs):
    return hasattr(arg, "send") and hasattr(arg, "throw") and hasattr(arg, "__next__")


def checking_typing_literal(arg, possible_types, *args, **kwargs):
    return arg in possible_types


def checking_typing__validator(arg, possible_types, *args, **kwargs):
    """
    required to support python versions 3.7, 3.8
    """
    return checking_typing_validator(arg, possible_types, *args, **kwargs)


def checking_typing_validator(arg, possible_types, *args, **kwargs):
    if len(possible_types) == 2:
        default_return = empty
        required_type, validation = possible_types
    else:
        required_type, validation, default_return = possible_types
    if validation(arg) is False:
        if default_return is not empty:
            default_return_queue.put(default_return)
            return None
        if isinstance(validation, partial):
            validation = validation.func
        validation_function_file = inspect.getfile(validation)
        validation_body, validation_line = inspect.getsourcelines(validation)
        raise ValidationError(
            f"Argument: `{arg}` did not pass the validation defined here "
            f'\n\tFile: "{validation_function_file}", line {validation_line}'
            f"\n\tName: {validation.__name__}"
        )
    try:
        return isinstance(arg, required_type)
    except TypeError:
        return check_type(arg, required_type, **kwargs)


def checking_typing__itervalidator(arg, possible_types, *args, **kwargs):
    """
    required to support python versions 3.7, 3.8
    """
    return checking_typing_itervalidator(arg, possible_types, *args, **kwargs)


def checking_typing_itervalidator(arg, possible_types, *args, **kwargs):
    required_type, validation = possible_types
    return check_type(arg, required_type, validation_with=validation, **kwargs)


def checking_typing_iterable(arg: Any, possible_types: tuple, *args, **kwargs):
    if not hasattr(arg, "__iter__"):
        return False
    pssble_type = possible_types[0]
    return all(check_type(argument, pssble_type, **kwargs) for argument in arg)


def module_checking_typing_list(arg: Any, possible_types: Any):
    if (
        not hasattr(possible_types, "__args__")
        or not possible_types.__args__
        or all(isinstance(pt, TypeVar) for pt in possible_types.__args__)
    ):
        return isinstance(arg, list)
    return bool(list_elements(arg, possible_types))


def module_checking_typing_dict(arg: Any, possible_types: Any):
    if (
        not hasattr(possible_types, "__args__")
        or not possible_types.__args__
        or all(isinstance(pt, TypeVar) for pt in possible_types.__args__)
    ):
        return isinstance(arg, dict)
    return bool(dict_elements(arg, possible_types))


def module_checking_typing_set(arg: Any, possible_types: Any):
    if (
        not hasattr(possible_types, "__args__")
        or isinstance(possible_types.__args__[0], TypeVar)
        or all(isinstance(pt, TypeVar) for pt in possible_types.__args__)
    ):
        return isinstance(arg, set)
    return bool(set_elements(arg, possible_types))


def module_checking_typing_tuple(arg: Any, possible_types: Any):
    if (
        not hasattr(possible_types, "__args__")
        or not possible_types.__args__
        or all(isinstance(pt, TypeVar) for pt in possible_types.__args__)
    ):
        return isinstance(arg, tuple)
    return bool(tuple_elements(arg, possible_types))


def validate_object(value, validation_func=None):
    if validation_func:
        return validation_func(value)
    return True


supported_typings = vars()
if extension_module:
    m = [f"module_checking_typing_{t}" for t in ("list", "dict", "set", "tuple")]
    supported_modules = {k: v for k, v in vars().items() if k in m}
else:
    supported_modules = {}


def check_type(argument, type_of, mro=False, **kwargs):
    # if int(py_version) >= 10 and isinstance(type_of, (str, bytes)):
    #     type_of = eval(type_of, locals(), globals())
    if checking_typing_generator(argument, type_of):
        # generator will be exhausted when we check it, so we return it without any checking
        return argument

    if checking_typing_generator(argument, type_of):
        # generator will be exhausted when we check it, so we return it without any checking
        return argument

    check_result = True
    if type_of is not None:
        origin, origin_name = get_origins(type_of)
        origin_name = origin_name.lower()

        if "any" in origin_name:
            return validate_object(argument, kwargs.get("validation_with"))
        if "json" in origin_name or "json" in str(type_of):
            return supported_typings["checking_typing_json"](argument, type_of, mro)

        try:
            return supported_modules[f"module_checking_typing_{origin_name}"](argument, type_of)
        except KeyError:
            pass

        if "new_type" in origin_name:
            type_of = type_of.__supertype__
            origin, origin_name = get_origins(type_of)
            origin_name = origin_name.lower()

        if isinstance(type_of, typing_base_class) or (py_version >= 3.9 and origin is not None):
            try:
                return supported_typings[f"checking_typing_{origin_name}"](
                    argument, get_possible_types(type_of), mro, **kwargs
                )
            except AttributeError:
                return isinstance(argument, type_of.__args__)
        elif isinstance(type_of, str):
            return argument.__class__.__name__ == type_of
        elif mro:
            if origin_name == "union":
                possible_types = get_possible_types(type_of)
                return supported_typings[f"checking_typing_{origin_name}"](
                    argument, possible_types, mro
                )
            return type_of in argument
        else:
            try:
                is_instance = isinstance(argument, type_of)
            except TypeError:
                return isinstance(argument, type_of._subs_tree()[1:])
            else:
                if not is_instance:
                    return False
                return validate_object(argument, kwargs.get("validation_with"))
    return check_result
