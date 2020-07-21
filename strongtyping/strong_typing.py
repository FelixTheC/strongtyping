#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 28.04.20
@author: felix
"""
import inspect
import sys
from collections.abc import Generator
from functools import lru_cache
from itertools import zip_longest
from functools import wraps
import typing
import warnings

from typing import Any
from typing import TypeVar

from strongtyping._utils import _get_new
from easy_property import action
from strongtyping._utils import _severity_level
from strongtyping._utils import remove_subclass
from strongtyping.cached_set import CachedSet


class TypeMisMatch(AttributeError):
    def __init__(self, message):
        super().__init__()
        print(message)


py_version = sys.version_info.minor
typing_base_class = typing._GenericAlias if hasattr(typing, '_GenericAlias') else typing.GenericMeta


@lru_cache(maxsize=1024)
def get_possible_types(typ_to_check) -> typing.Union[tuple, None]:
    """
    :param typ_to_check: some typing like List[str], Dict[str, int], Tuple[Union[str, int], List[int]]
    :return: the inner types, classes of the type
        - List[str] = (str, )
        - Dict[str, int] = (str, int, )
        - Tuple[Union[str, int], List[int]] = (Union[str, int], List[int], )
    """
    if typ_to_check.__args__ is not None:
        return tuple(typ for typ in typ_to_check.__args__ if not isinstance(typ, TypeVar))


def get_origins(typ_to_check: any) -> tuple:
    """
    :param typ_to_check: typ_to_check: some typing like List[str], Dict[str, int], Tuple[Union[str, int], List[int]]
    :return: the class, alias_class and the class name
        - List[str] = (list, 'List')
        - Dict[str, int] = (dict, 'Dict')
        - Tuple[Union[str, int], List[int]] = (tuple, 'Tuple)
        - FunctionType = (None, 'None')
    """
    origin = None
    if hasattr(typ_to_check, '__origin__') or hasattr(typ_to_check, '__orig_bases__'):
        origin = typ_to_check.__origin__ if typ_to_check.__origin__ is not None else typ_to_check.__orig_bases__
    if py_version == 6 and hasattr(typ_to_check, '_gorg'):
        return None, str(typ_to_check._gorg).replace('typing.', '')
    return origin, origin._name if hasattr(origin, '_name') else \
        typ_to_check._name if hasattr(typ_to_check, '_name') else str(origin).replace('typing.', '')


def checking_typing_dict(arg: Any, possible_types: tuple, *args):
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


def checking_typing_set(arg: Any, possible_types: tuple, *args):
    try:
        pssble_type = possible_types[0]
    except (TypeError, IndexError):
        return isinstance(arg, set)
    else:
        return isinstance(arg, set) and all(check_type(argument, pssble_type) for argument in arg)


def checking_typing_type(arg: Any, possible_types: tuple, *args):
    try:
        arguments = arg.__mro__
    except AttributeError:
        return False
    else:
        return any(check_type(arguments, possible_type, mro=True) for possible_type in possible_types)


def checking_typing_union(arg: Any, possible_types: tuple, mro):
    if mro:
        return any(pssble_type in arg for pssble_type in possible_types)
    try:
        return isinstance(arg, possible_types)
    except TypeError:
        return any(check_type(arg, typ) for typ in possible_types)


def checking_typing_iterator(arg: Any, *args):
    return hasattr(arg, '__iter__') and hasattr(arg, '__next__')


def checking_typing_callable(arg: Any, possible_types: tuple, *args):
    insp = inspect.signature(arg)
    return_val = insp.return_annotation == possible_types[-1]
    params = insp.parameters
    return return_val and all(p.annotation == pt for p, pt in zip(params.values(), possible_types))


def checking_typing_tuple(arg: Any, possible_types: tuple, *args):
    if possible_types is None:
        return isinstance(arg, tuple)
    if len(possible_types) > 0 and not len(arg) == len(possible_types) or not isinstance(arg, tuple):
        return False
    return all(check_type(argument, typ) for argument, typ in zip(arg, possible_types))


def checking_typing_list(arg: Any, possible_types: tuple, *args):
    if not isinstance(arg, list):
        return False
    return all(check_type(argument, typ) for argument, typ in zip_longest(arg, possible_types,
                                                                          fillvalue=possible_types[0]))


def checking_typing_json(arg, possible_types, *args):
    try:
        possible_types.dumps(arg)
    except TypeError:
        return isinstance(arg, str)
    else:
        return True


def checking_typing_generator(arg, possible_types, *args):
    return isinstance(arg, Generator)


def checking_typing_literal(arg, possible_types, *args):
    return arg in possible_types


supported_typings = vars()


def check_type(argument, type_of, mro=False):
    check_result = True
    if type_of is not None:
        origin, origin_name = get_origins(type_of)
        origin_name = origin_name.lower()

        if 'any' in origin_name or 'any' in str(type_of).lower():
            return check_result
        if 'json' in origin_name or 'json' in str(type_of):
            return supported_typings['checking_typing_json'](argument, type_of, mro)

        if 'new_type' in origin_name:
            if '3.6' in sys.version:
                return check_result
            type_of = type_of.__supertype__
            origin, origin_name = get_origins(type_of)
            origin_name = origin_name.lower()
        if isinstance(type_of, typing_base_class):
            try:
                possible_types = get_possible_types(type_of)
                return supported_typings[f'checking_typing_{origin_name}'](argument, possible_types, mro)
            except AttributeError:
                return isinstance(argument, type_of.__args__)
        elif isinstance(type_of, str):
            return argument.__class__.__name__ == type_of
        elif mro:
            if origin_name == 'union':
                possible_types = get_possible_types(type_of)
                return supported_typings[f'checking_typing_{origin_name}'](argument, possible_types, mro)
            return type_of in argument
        else:
            try:
                return isinstance(argument, type_of)
            except TypeError:
                return isinstance(argument, type_of._subs_tree()[1:])
    return check_result


def match_typing(_func=None, *, excep_raise: Exception = TypeMisMatch, cache_size=0,
                 subclass: bool = False, severity='env', **kwargs):
    cached_set = None if cache_size == 0 else CachedSet(cache_size)

    def wrapper(func):
        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__

        severity_level = _severity_level(severity)

        @wraps(func)
        def inner(*args, **kwargs):
            if arg_names and severity_level > 0:

                args = remove_subclass(args, subclass)

                if cached_set is not None:
                    # check if func with args and kwargs was checked once before with positive result
                    cached_key = (func, args.__str__(), kwargs.__str__())
                    if cached_key in cached_set:
                        return func(*args, **kwargs)

                # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
                failed_params = tuple(
                    arg_name for arg, arg_name in zip(args, arg_names) if not check_type(arg, annotations.get(arg_name))
                )
                failed_params += tuple(
                    kwarg_name for kwarg_name, kwarg in kwargs.items() if not check_type(kwarg,
                                                                                         annotations.get(kwarg_name))
                )

                if failed_params:
                    msg = f'Incorrect parameters: {", ".join(f"{name}: {annotations[name]}" for name in failed_params)}'

                    if excep_raise is not None and severity_level == 1:
                        raise excep_raise(msg)
                    else:
                        warnings.warn(msg, RuntimeWarning)

                if cached_set is not None:
                    cached_set.add(cached_key)
            return func(*args, **kwargs)

        inner.__fe_strng_mtch__ = 0
        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper


def match_class_typing(_cls=None, *, excep_raise: Exception = TypeError, cache_size=0, severity='env', **kwargs):

    def wrapper(cls):

        severity_level = _severity_level(severity)

        def inner(*args, **kwargs):
            if severity_level > 0:
                cls.__new__ = _get_new(match_typing, excep_raise, cache_size, severity, **kwargs)
                if hasattr(cls.__init__, '__annotations__'):
                    cls.__init__ = match_typing(cls.__init__)
            return cls(*args, **kwargs)

        return inner

    if _cls is not None:
        return wrapper(_cls)
    else:
        return wrapper


def action(f, frefs):
    """
    This code is original from Ruud van der Ham https://github.com/salabim/easy_property
    """
    if f.__qualname__ == action.qualname:
        if any(action.f[fref] is not None for fref in frefs.split("_")):
            raise AttributeError(f"decorator defined twice")
    else:
        action.f.update({}.fromkeys(action.f, None))  # reset all values to None
        action.qualname = f.__qualname__
    action.f.update({}.fromkeys(frefs.split('_'), f))  # set all frefs values to f

    # this line was added by myself
    action.f['setter'] = match_typing(action.f['setter']) if action.f['setter'] is not None else None

    return property(*(action.f[ref] if (ref != "documenter" or action.f[ref] is None)
                      else action.f[ref](0) for ref in action.f))


action.qualname = None
action.f = dict.fromkeys(["getter", "setter", "deleter", "documenter"], None)


def getter(func):
    return action(func, 'getter')


def setter(func):
    return action(func, 'setter')


def getter_setter(func):
    return action(func, 'getter_setter')
