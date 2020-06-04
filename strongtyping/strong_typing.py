#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 28.04.20
@author: felix
"""
import functools
from itertools import zip_longest
import typing


class TypeMisMatch(AttributeError):
    def __init__(self, message):
        super().__init__()
        print(message)


def check_type(argument, type_of):
    check_result = True
    if type_of is not None:
        if isinstance(type_of, typing._GenericAlias):
            if type_of._name is not None:
                check_result = isinstance(argument, type_of.__origin__) and \
                               all([check_type(arg, typ) for arg, typ in zip_longest(argument, type_of.__args__)]) and \
                               len(argument) == len(type_of.__args__)
            else:
                check_result = isinstance(argument, type_of.__args__)
        elif isinstance(type_of, str):
            check_result = argument.__class__.__name__ == type_of
        else:
            check_result = isinstance(argument, type_of)
    return check_result


def match_typing(_func=None, *, excep_raise: Exception = TypeMisMatch):

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            is_class_function = hasattr(args[0], '__weakref__') if len(args) > 0 else False
            self, args = (args[0], args[1:]) if is_class_function else (None, args)
            parameter_types = func.__annotations__

            check_kwargs = all([check_type(val, parameter_types.get(key, None)) for key, val in kwargs.items()])
            check_args = all([check_type(arg, typ) for arg, typ in zip(args, parameter_types.values())])

            if check_kwargs and check_args:
                args = [self, *args] if is_class_function else args
                return func(*args, **kwargs)
            else:
                params = [f'{key}: {val}' for key, val in parameter_types.items() if key != 'return']
                msg = f'Parameters must have following type: {";".join(params)}'
                try:
                    raise excep_raise(message=msg)
                except TypeError:
                    raise excep_raise

        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper
