#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 19.11.20
@author: felix
"""
import inspect
import os
import typing
from collections import deque
from collections.abc import Callable, Iterable
from functools import lru_cache, partial
from queue import Queue
from typing import Any, TypeVar, _GenericAlias, _SpecialForm, _type_repr  # type: ignore

from strongtyping._utils import ORIGINAL_DUCK_TYPES, install_st_m

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
    def __init__(self, message, failed_params=None, param_values=None, annotations=None):
        super().__init__()
        print(message)


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        print(message)


typing_base_class = typing._GenericAlias  # type: ignore


@lru_cache(maxsize=1024)
def get_possible_types(typ_to_check, origin_name: str = "") -> typing.Union[tuple, None]:
    """
    :param typ_to_check: some typing like List[str], Dict[str, int], Tuple[Union[str, int], List[int]]
    :param origin_name: the name of the origin
    :return: the inner types, classes of the type
        - List[str] = (str, )
        - Dict[str, int] = (str, int, )
        - Tuple[Union[str, int], List[int]] = (Union[str, int], List[int], )
    """
    if origin_name == "typeddict":
        # we can ensure now that we use a python version which has typing.TypedDict
        return typ_to_check

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
    from strongtyping.strong_typing import MatchTypedDict

    """
    :param typ_to_check: typ_to_check: some typing like List[str], Dict[str, int], Tuple[Union[str, int], List[int]]
    :return: the class, alias_class and the class name
        - List[str] = (list, 'List')
        - Dict[str, int] = (dict, 'Dict')
        - Tuple[Union[str, int], List[int]] = (tuple, 'Tuple)
        - FunctionType = (None, 'None')
    """
    origin, origin_name = None, ""

    if isinstance(typ_to_check, MatchTypedDict):
        return typ_to_check, typ_to_check.__class__.__name__

    if hasattr(typ_to_check, "__annotations__") and hasattr(typ_to_check, "__orig_bases__"):
        if typ_to_check.__orig_bases__:
            orig_base = typ_to_check.__orig_bases__[0].__name__
        else:
            orig_base = typ_to_check.cls.__class__.__name__
        return typ_to_check, orig_base

    if typing.is_typeddict(typ_to_check):
        return typ_to_check, typ_to_check.__class__.__name__

    if hasattr(typ_to_check, "__origin__") or hasattr(typ_to_check, "__orig_bases__"):
        if hasattr(typ_to_check, "__origin__") and hasattr(typ_to_check.__origin__, "__name__"):
            origin = typ_to_check.__origin__
            origin_name = origin.__name__
        elif hasattr(typ_to_check, "__origin__") or hasattr(typ_to_check, "__orig_bases__"):
            if hasattr(typ_to_check, "__origin__") and typ_to_check.__origin__ is not None:
                origin = typ_to_check.__origin__
            else:
                origin = typ_to_check.__orig_bases__

    if hasattr(origin, "_name"):
        origin_name = origin._name  # type: ignore
    else:
        if hasattr(typ_to_check, "_name"):
            origin_name = typ_to_check._name if typ_to_check._name is not None else origin_name
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


def checking_typing_optional(arg: Any, possible_types: tuple, mro, **kwargs):
    return arg is None or check_type(arg, possible_types[0])


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


def checking_typing_itervalidator(arg, possible_types, *args, **kwargs):
    required_type, validation = possible_types
    return check_type(arg, required_type, validation_with=validation, **kwargs)


def checking_typing_iterable(arg: Any, possible_types: tuple, *args, **kwargs):
    if not hasattr(arg, "__iter__"):
        return False
    pssble_type = possible_types[0]
    return all(check_type(argument, pssble_type, **kwargs) for argument in arg)


def checking_typing_typedict_values(args: dict, required_types: dict, total: bool):
    if total:
        return all(check_type(args.get(key), val) for key, val in required_types.items())
    fields_to_check = {key: val for key, val in required_types.items() if key in args}
    return all(check_type(args[key], val) for key, val in fields_to_check.items())


def checking_typing_class(arg: Any, possible_types: tuple, *args, **kwargs):
    return isinstance(arg, possible_types)


def checking_typing_typeddict(arg: Any, possible_types: Any, *args, **kwargs):
    total = possible_types.__total__
    required_fields = possible_types.__annotations__
    if total:
        if not all(field in arg for field in required_fields):
            return False
    return checking_typing_typedict_values(arg, required_fields, total)


def checking_typing_typeddict_required(arg: Any, possible_types: Any, *args, **kwargs):
    return check_type(arg, possible_types[0])


def checking_typing_typeddict_notrequired(arg: Any, possible_types: Any, *args, **kwargs):
    if arg is None:
        return True
    return check_type(arg, possible_types[0])


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


def module_checking_typing_validator(arg, possible_types, *args, **kwargs):
    try:
        required_type, validation = possible_types.__args__
    except ValueError:
        required_type, validation, _ = possible_types.__args__
    if validation(arg) is False:
        if isinstance(validation, partial):
            validation = validation.func
        validation_function_file = inspect.getfile(validation)
        validation_body, validation_line = inspect.getsourcelines(validation)
        raise ValidationError(
            f"Argument: `{arg}` did not pass the validation defined here "
            f'\n\tFile: "{validation_function_file}", line {validation_line}'
            f"\n\tName: {validation.__name__}"
        )
    return check_type(arg, required_type, **kwargs)


def validate_object(value, validation_func=None):
    if validation_func:
        return validation_func(value)
    return True


def check_duck_typing(arg, possible_types, *args, **kwargs):
    if isinstance(arg, possible_types):
        return True

    if type(arg) in ORIGINAL_DUCK_TYPES:
        return possible_types in ORIGINAL_DUCK_TYPES[type(arg)]

    if "__mro__" not in dir(arg.__class__):
        arg_mros = set(arg.__class__.mro()[:-1])  # to exclude `object`
    else:
        arg_mros = set(arg.mro()[:-1])

    required_mros = set(possible_types.mro()[:-1])
    return arg_mros.issuperset(required_mros)


supported_typings = vars()


def check_type(argument, type_of, mro=False, **kwargs):
    from strongtyping.types import IterValidator, Validator

    # if int(py_version) >= 10 and isinstance(type_of, (str, bytes)):
    #     type_of = eval(type_of, locals(), globals())
    if checking_typing_generator(argument, type_of):
        # generator will be exhausted when we check it, so we return it without any checking
        return argument

    check_result = True
    if type_of is not None:
        origin, origin_name = get_origins(type_of)
        origin_name = origin_name.lower()

        if "new_type" in origin_name:
            type_of = type_of.__supertype__
            origin, origin_name = get_origins(type_of)
            origin_name = origin_name.lower()

        if kwargs.pop("check_duck_typing", None):
            return check_duck_typing(argument, type_of)

        if "any" in origin_name:
            return validate_object(argument, kwargs.get("validation_with"))
        if "json" in origin_name or "json" in str(type_of):
            return checking_typing_json(argument, type_of, mro)

        if origin is typing.Union:
            return checking_typing_union(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin in (list, typing.MutableSequence, typing.Deque, deque):
            if extension_module:
                return module_checking_typing_list(argument, type_of)
            return checking_typing_list(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin in (typing.Iterable, Iterable):
            return checking_typing_iterable(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is set:
            if extension_module:
                return module_checking_typing_set(argument, type_of)
            return checking_typing_set(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is tuple:
            if extension_module:
                return module_checking_typing_tuple(argument, type_of)
            return checking_typing_tuple(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin in (
            dict,
            typing.MutableMapping,
            typing.Dict,
            typing.DefaultDict,
            typing.OrderedDict,
            typing.Counter,
            typing.ChainMap,
        ):
            if extension_module:
                return module_checking_typing_dict(argument, type_of)
            return checking_typing_dict(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin in (typing.Callable, Callable):
            return checking_typing_callable(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is type:
            return checking_typing_type(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is Validator:
            if extension_module:
                return module_checking_typing_validator(argument, type_of)
            return checking_typing_validator(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is IterValidator:
            return checking_typing_itervalidator(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is typing.Literal:
            return checking_typing_literal(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif isinstance(type_of, str):
            return argument.__class__.__name__ == type_of
        elif origin_name in ("_typeddictmeta", "matchtypeddict", "typeddict"):
            return checking_typing_typeddict(argument, get_possible_types(type_of, "typeddict"))
        elif origin_name == "required":
            return checking_typing_typeddict_required(
                argument, get_possible_types(type_of, origin_name)
            )
        elif origin_name == "notrequired":
            return checking_typing_typeddict_notrequired(
                argument, get_possible_types(type_of, origin_name)
            )
        elif mro:
            if origin_name == "union":
                possible_types = get_possible_types(type_of)
                return supported_typings[f"checking_typing_{origin_name}"](
                    argument, possible_types, mro
                )
            return type_of in argument
        else:
            try:
                is_instance = isinstance(argument, type_of) or argument == type_of
            except (TypeError, AttributeError):
                return isinstance(argument, type_of._subs_tree()[1:])
            else:
                if not is_instance:
                    return False
                return validate_object(argument, kwargs.get("validation_with"))
    return check_result
