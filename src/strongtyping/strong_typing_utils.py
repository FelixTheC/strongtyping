#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 19.11.20
@author: felix
"""

import inspect
import types
import typing
from collections import deque
from collections.abc import Callable, Iterable
from functools import lru_cache, partial
from queue import Queue
from typing import Any, TypeVar

from strongtyping._utils import ORIGINAL_DUCK_TYPES
from strongtyping.exceptions import ValidationError

empty = object()
default_return_queue: Queue[Any] = Queue()

T = TypeVar("T")

typing_base_class = typing._GenericAlias  # type: ignore


@lru_cache(maxsize=1024)
def get_possible_types(typ_to_check: Any, origin_name: str = "") -> Any:
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

    if hasattr(typ_to_check, "__args__") and typ_to_check.__args__ is not None:
        return tuple(typ for typ in typ_to_check.__args__ if not isinstance(typ, TypeVar))
    else:
        return None


@lru_cache(maxsize=1024)
def get_origins(typ_to_check: Any) -> tuple[Any, str]:
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

    if hasattr(typ_to_check, "__class__") and typ_to_check.__class__.__name__ == "_AnyMeta":
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


def checking_typing_dict(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
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


def checking_typing_set(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    if not possible_types:
        return isinstance(arg, set)
    possible_type = possible_types[0]
    return isinstance(arg, set) and all(
        check_type(argument, possible_type, **kwargs) for argument in arg
    )


def checking_typing_type(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
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


def checking_typing_union(arg: Any, possible_types: Any, mro: bool, **kwargs: Any) -> bool:
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


def checking_typing_optional(arg: Any, possible_types: Any, mro: bool, **kwargs: Any) -> bool:
    return arg is None or check_type(arg, possible_types[0])


def checking_typing_iterator(arg: object, *args: Any, **kwargs: Any) -> bool:
    return hasattr(arg, "__iter__") and hasattr(arg, "__next__")


def checking_typing_callable(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    insp = inspect.signature(arg)
    return_val = insp.return_annotation == possible_types[-1]
    params = insp.parameters
    return return_val and all(p.annotation == pt for p, pt in zip(params.values(), possible_types))


def checking_typing_tuple(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    if not possible_types:
        return isinstance(arg, tuple)
    if Ellipsis in possible_types and isinstance(arg, tuple):
        if not arg:
            return True
        return checking_ellipsis(arg, possible_types, **kwargs)
    if not isinstance(arg, tuple) or not (len(arg) == len(possible_types)):
        return False
    return all(check_type(argument, typ, **kwargs) for argument, typ in zip(arg, possible_types))


def checking_typing_list(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    if not isinstance(arg, list):
        return False
    if isinstance(arg, list) and not possible_types:
        return True
    return all(check_type(argument, possible_types[0], **kwargs) for argument in arg)


def checking_ellipsis(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    possible_types = [pt for pt in possible_types if pt is not Ellipsis]
    return all(check_type(argument, possible_types[0], **kwargs) for argument in arg)


def checking_typing_json(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    try:
        possible_types.dumps(arg)
    except TypeError:
        return isinstance(arg, str)
    else:
        return True


def checking_typing_generator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    return hasattr(arg, "send") and hasattr(arg, "throw") and hasattr(arg, "__next__")


def checking_typing_literal(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    return arg in possible_types


def checking_typing_validator(
    arg: Any, possible_types: Any, *args: Any, **kwargs: Any
) -> bool | None:
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
        res_is: bool = isinstance(arg, required_type)
        return res_is
    except TypeError:
        res_ct: bool = check_type(arg, required_type, **kwargs)
        return res_ct


def checking_typing_itervalidator(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    required_type, validation = possible_types
    res: bool = check_type(arg, required_type, validation_with=validation, **kwargs)
    return res


def checking_typing_iterable(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    if not hasattr(arg, "__iter__"):
        return False
    pssble_type = possible_types[0]
    return all(check_type(argument, pssble_type, **kwargs) for argument in arg)


def checking_typing_typedict_values(
    args: dict[Any, Any], required_types: dict[Any, Any], total: bool
) -> bool:
    if total:
        return all(check_type(args.get(key), val) for key, val in required_types.items())
    fields_to_check = {key: val for key, val in required_types.items() if key in args}
    return all(check_type(args[key], val) for key, val in fields_to_check.items())


def checking_typing_class(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    return isinstance(arg, possible_types)


def checking_typing_typeddict(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    total = getattr(possible_types, "__total__", True)
    required_fields = getattr(possible_types, "__annotations__", {})
    res: bool = checking_typing_typedict_values(arg, required_fields, total)
    return res


def checking_typing_typeddict_required(
    arg: Any, possible_types: Any, *args: Any, **kwargs: Any
) -> bool:
    res: bool = check_type(arg, possible_types[0])
    return res


def checking_typing_typeddict_notrequired(
    arg: Any, possible_types: Any, *args: Any, **kwargs: Any
) -> bool:
    if arg is None:
        return True
    res: bool = check_type(arg, possible_types[0])
    return res


def checking_typing_unpack(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    if typing.is_typeddict(possible_types[0]) and isinstance(arg, dict):
        typed_dict_obj: Any = possible_types[0]
        return all(
            check_type(arg.get(key), required_type)
            for key, required_type in typed_dict_obj.__annotations__.items()
        )
    return False


def validate_object(value: Any, validation_func: Callable[[Any], bool] | None = None) -> bool:
    if validation_func:
        return validation_func(value)
    return True


def check_duck_typing(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
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


def check_typevar(arg: Any, possible_types: Any, *args: Any, **kwargs: Any) -> bool:
    if possible_types.__bound__:
        res_b: bool = check_type(arg, possible_types.__bound__)
        return res_b
    elif possible_types.__constraints__:
        res_c: bool = check_type(arg, possible_types.__constraints__)
        return res_c
    return True


supported_typings = vars()


def check_annotated_type(argument: Any, type_of: Any) -> bool:
    result = True  # when no callable is assigned to __metadata__ we return True
    for func_obj in type_of.__metadata__:
        if callable(func_obj):
            result = result and func_obj(argument)

    return result


def check_type(argument: Any, type_of: Any, mro: bool = False, **kwargs: Any) -> Any:
    from strongtyping.st_types import IterValidator, Validator
    from strongtyping.strong_typing import MatchTypedDict

    # if int(py_version) >= 10 and isinstance(type_of, (str, bytes)):
    #     type_of = eval(type_of, locals(), globals())
    if checking_typing_generator(argument, type_of):
        # generator will be exhausted when we check it, so we return it without any checking
        return argument

    check_result = True

    arg_type = type(argument)
    if type_of is int and arg_type is int:
        return True
    if type_of is str and arg_type is str:
        return True
    if type_of is bool and arg_type is bool:
        return True

    if type_of is not None:
        origin, origin_name = get_origins(type_of)
        origin_name = origin_name.lower()

        if isinstance(type_of, TypeVar):
            return check_typevar(argument, type_of)

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
        elif isinstance(type_of, types.UnionType):
            # Handle PEP 604 union syntax (e.g., int | str)
            return checking_typing_union(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin in (list, typing.MutableSequence, typing.Deque, deque):
            return checking_typing_list(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin in (typing.Iterable, Iterable):
            return checking_typing_iterable(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is set:
            return checking_typing_set(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is tuple:
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
            MatchTypedDict,
        ):
            possible_type = get_possible_types(type_of, origin_name)
            return checking_typing_dict(argument, possible_type, mro, **kwargs)
        elif origin in (typing.Callable, Callable):
            return checking_typing_callable(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is type:
            return checking_typing_type(
                argument, get_possible_types(type_of, origin_name), mro, **kwargs
            )
        elif origin is Validator:
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
        elif origin_name == "unpack":
            return checking_typing_unpack(argument, get_possible_types(type_of, origin_name))
        elif origin_name == "readonly":
            sub_type = get_possible_types(type_of, origin_name)
            return check_type(argument, sub_type)
        elif origin_name == "annotated":
            return check_annotated_type(argument, type_of)
        elif origin_name == "typeguard":
            return check_type(argument, get_possible_types(type_of, origin_name), mro, **kwargs)
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
                if callable(type_of):
                    return type_of(argument) is not None
                return isinstance(argument, type_of._subs_tree()[1:])
            else:
                if not is_instance:
                    return False
                return validate_object(argument, kwargs.get("validation_with"))
    return check_result
