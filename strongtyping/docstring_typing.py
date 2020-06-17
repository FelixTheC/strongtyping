#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 11.06.20
@author: felix
"""
import functools
from datetime import datetime
import inspect
import typing
import builtins
import re
from typing import _GenericAlias

from cached_set import CachedSet
from strong_typing import TypeMisMatch

TYPE_EXTRACTION_PATTERN = r'^(:\D+:)'
# PATTERN_1 = r'[()]'
PATTERN_1 = r''
EXTRACT_PARAM_NAME_PATTERN = r'(?::type\W)'


def separate_param_type(docstring_type_part: str) -> tuple:
    t = re.split(TYPE_EXTRACTION_PATTERN, docstring_type_part)
    clean = [re.sub(PATTERN_1, '', part.strip()) for part in t if part]
    return re.sub(EXTRACT_PARAM_NAME_PATTERN, '', clean[0]).replace(':', ''), clean[1]


def param_attr(attr: str):
    try:
        return getattr(typing, attr)
    except AttributeError:
        return getattr(builtins, attr)


def is_tuple(arg, type_of):
    print(type_of)
    print(re.findall(r'\w{2,}', type_of))
    try:
        return all(isinstance(a, param_attr(t)) for a, t in zip(arg, re.findall(r'\w{2,}', type_of)))
    except TypeError:
        return False


options = {
    '(': is_tuple
}


def check_doc_str_type(arg, type_of):
    check_result = True
    if type_of is not None:
        try:
            return options[type_of[0]](arg, type_of[1:-1])
        except KeyError:
            try:
                return isinstance(arg, tuple(map(param_attr, re.findall(r'\w{2,}', type_of))))
            except AttributeError:
                return arg.__class__.__name__ == type_of

    return check_result


def match_docstring(_func=None, *, excep_raise: Exception = TypeMisMatch, cache_size=0):
    cached_set = None if cache_size == 0 else CachedSet(cache_size)

    def wrapper(func):
        docstring = [separate_param_type(string) for string in inspect.getdoc(func).split('\n') if string[:5] == ':type']
        docstring_types = {ds[0]: ds[1] for ds in docstring}

        @functools.wraps(func)
        def inner(*args, **kwargs):

            if cached_set is not None:
                # check if func with args and kwargs was checked once before with positive result
                cached_key = (func, args.__str__(), kwargs.__str__())
                if cached_key in cached_set:
                    return func(*args, **kwargs)

            # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
            failed_params = tuple(
                arg_name for arg, arg_name in zip(args, docstring_types) if not check_doc_str_type(arg,
                                                                                                   docstring_types.get(arg_name))
            )
            failed_params += tuple(
                kwarg_name for kwarg_name, kwarg in kwargs.items() if not check_doc_str_type(kwarg,
                                                                                             docstring_types.get(kwarg_name))
            )

            if failed_params:
                raise excep_raise(
                    f'Incorrect parameters: {", ".join(f"{name}: {docstring_types[name]}" for name in failed_params)}'
                )

            if cached_set is not None:
                cached_set.add(cached_key)

            return func(*args, **kwargs)

        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper


# if __name__ == '__main__':
#     from pprint import pprint
#     print(inspect.signature(func_a).parameters)
#     docstring = [separate_param_type(string) for string in inspect.getdoc(func_a).split('\n') if string[:5] == ':type']
#     docstring_types = {ds[0]: ds[1] for ds in docstring}
#     print(docstring_types)
#     args = []
#     for elem in map(param_attr, re.split(r'\b', 'List[Tuple[Union[str, int], Union[str, int]]]')):
#         if elem is not None:
#             args.append(elem)
#     print(args)
#     func_a([1, 2, 3])
