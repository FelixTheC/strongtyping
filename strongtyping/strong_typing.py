#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 28.04.20
@author: felix
"""
import functools
import inspect
from itertools import zip_longest
import typing

from strongtyping.cached_set import CachedSet


class TypeMisMatch(AttributeError):
    def __init__(self, message):
        super().__init__()
        print(message)


typing_base_class = typing._GenericAlias if hasattr(typing, '_GenericAlias') else typing.GenericMeta


def get_possible_types(typ_to_check) -> typing.Union[tuple, None]:
    typ_check_args = typ_to_check.__args__
    if typ_check_args is not None:
        return tuple(typ for typ in typ_check_args if not isinstance(typ, typing.TypeVar))


def get_fillvalue(typ_to_check: any, return_val: any) -> typing.Union[str, int, None]:
    if hasattr(typ_to_check, '_name'):
        return return_val if typ_to_check._name == 'List' else None


def get_origins(typ_to_check: any) -> tuple:
    origin = None
    if hasattr(typ_to_check, '__origin__') or hasattr(typ_to_check, '__orig_bases__'):
        origin = typ_to_check.__origin__ if typ_to_check.__origin__ is not None else typ_to_check.__orig_bases__
    return origin, origin._name if hasattr(origin, '_name') else\
        typ_to_check._name if hasattr(typ_to_check, '_name') else f'{typ_to_check}'


def check_typing_dict(arg: typing.Any, possible_types: tuple):
    if not isinstance(arg, dict):
        return False
    key, val = possible_types
    if hasattr(key, '__origin__'):
        result_key = all(check_type(a, key) for a in arg.keys())
    else:
        result_key = all(isinstance(k, key) for k in arg.keys())
    if hasattr(val, '__origin__'):
        result_val = all(check_type(a, val) for a in arg.values())
    else:
        result_val = all(isinstance(v, val) for v in arg.values())
    return result_key and result_val


def checking_typing_set(arg: typing.Any, possible_types: tuple):
    pssble_type = possible_types[0]
    return all(check_type(argument, pssble_type) for argument in arg)


def checking_typing_type(arg: typing.Any, possible_types: tuple):
    if not hasattr(arg, '__mro__'):
        return False
    arguments = arg.__mro__
    return any(check_type(arguments, possible_type, mro=True) for possible_type in possible_types)


def checking_typing_union(arg: typing.Any, possible_types: tuple, mro):
    if mro:
        return any(pssble_type in arg for pssble_type in possible_types)
    try:
        return isinstance(arg, possible_types)
    except TypeError:
        return all(check_type(arg, typ) for typ in possible_types)


def checking_typing_iterator(arg: typing.Any):
    return hasattr(arg, '__iter__') and hasattr(arg, '__next__')


def checking_typing_callable(arg: typing.Any, possible_types: tuple):
    insp = inspect.signature(arg)
    return_val = insp.return_annotation == possible_types[-1]
    params = insp.parameters
    return return_val and all(p.annotation == pt for p, pt in zip(params.values(), possible_types))


def check_type(argument, type_of, mro=False):
    check_result = True
    if type_of is not None:
        origin, origin_name = get_origins(type_of)
        if 'any' in origin_name.lower():
            return check_result
        if isinstance(type_of, typing_base_class):
            if hasattr(type_of, '__origin__'):
                possible_types = get_possible_types(type_of)

                if 'dict' in origin_name.lower():
                    return check_typing_dict(argument, possible_types)
                if 'set' in origin_name.lower():
                    return checking_typing_set(argument, possible_types)
                if 'type' in origin_name.lower():
                    return checking_typing_type(argument, possible_types)
                if 'iterator' in origin_name.lower():
                    return checking_typing_iterator(argument)
                if 'callable' in origin_name.lower():
                    return checking_typing_callable(argument, possible_types)

                if possible_types and origin_name != 'Union':
                    fillvalue = get_fillvalue(type_of, possible_types[0])
                    check_result = isinstance(argument, origin) and all(check_type(arg, typ) for arg, typ in
                                                                        zip_longest(argument, possible_types,
                                                                                    fillvalue=fillvalue)) and (
                                           len(argument) == len(type_of.__args__) or (isinstance(argument, list)))
                elif origin_name == 'Union':
                    return checking_typing_union(argument, possible_types, mro)
                else:
                    possible_type = origin[0] if isinstance(origin, (list, tuple)) else origin
                    check_result = isinstance(argument, possible_type)
            else:
                check_result = isinstance(argument, type_of.__args__)
        elif isinstance(type_of, str):
            check_result = argument.__class__.__name__ == type_of
        elif mro:
            check_result = type_of in argument
        else:
            try:
                check_result = isinstance(argument, type_of)
            except TypeError:
                check_result = isinstance(argument, type_of._subs_tree()[1:])
    return check_result


def match_typing(_func=None, *, excep_raise: Exception = TypeMisMatch, cache_size=0):
    cached_set = CachedSet(cache_size) if cache_size > 0 else None

    def wrapper(func):
        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__

        @functools.wraps(func)
        def inner(*args, **kwargs):

            if cached_set is not None:
                # check if func with args and kwargs was checked once before with positive result
                cached_key = (func, repr(args), repr(kwargs))
                if cached_key in cached_set:
                    return func(*args, **kwargs)

            # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
            failed_arg_names = tuple(
                arg_name for arg, arg_name in zip(args, arg_names) if not check_type(arg, annotations.get(arg_name))
            )
            failed_kwarg_names = tuple(
                kwarg_name for kwarg_name, kwarg in kwargs.items() if not check_type(kwarg, annotations.get(kwarg_name))
            )

            if failed_arg_names or failed_kwarg_names:
                params = [f"{name}: {annotations[name]}" for name in failed_arg_names + failed_kwarg_names]
                msg = f'Incorrect parameters: {", ".join(params)}'
                raise excep_raise(msg)

            if cached_set is not None:
                cached_set.add(cached_key)

            return func(*args, **kwargs)

        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper
