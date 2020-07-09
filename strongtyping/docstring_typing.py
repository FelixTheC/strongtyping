#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 11.06.20
@author: felix
"""
import functools
import inspect
import typing
import builtins
import re
import warnings
from types import FunctionType
from types import MethodType

from strongtyping.strong_typing import match_class_typing
from strongtyping.cached_set import CachedSet
from strongtyping.strong_typing import TypeMisMatch

TYPE_EXTRACTION_PATTERN = r'(^[:a-zA-Z0-9 _-]+(:))'
PATTERN_1 = r''
EXTRACT_PARAM_NAME_PATTERN = r'(?::(param|parameter|arg|argument|key|keyword|type|vartype)\W)'
TUPLE_PATTERN = r'\(([^)]+)\)'
PATTERN = r'[\(\)\[\[]'
OR_PATTERN = r'([\(\[]\w+)\W+(or)\W+(\w+)'
COMMA_PATTERN = r'([\(\[]\w+)\W+(\w+)'
REMOVE_PATTERN = r'[\(\[\)\]]'
FM_PATTERN = r'([FM][a-z]{5,7}Type)'


def separate_param_type(docstring_type_part: str) -> tuple:
    t = re.split(TYPE_EXTRACTION_PATTERN, docstring_type_part)
    clean = [re.sub(PATTERN_1, '', part.strip()) for part in t if part]
    return re.sub(EXTRACT_PARAM_NAME_PATTERN, '', clean[0]).replace(':', ''), clean[-1]


possible_types = {'(': tuple,
                  '[': list,
                  '{': set}


def generate_token(type_of) -> list:
    tokens = []
    start_token = False
    sub_list = []
    possible_sub_type = ''
    for p in type_of[1:-1].split():
        try:
            founded = re.search(PATTERN, p)
            item = founded.string.replace(',', '').strip()
            start_token = True if item[0] in ['(', '[', '{'] else False
            if start_token:
                possible_sub_type = item[0]
                sub_list.append(item[1:])
            if not start_token and sub_list:
                sub_list.append(item[:-1])
                tokens.append(possible_types[possible_sub_type]([param_attr(attr) for attr in sub_list]))
                sub_list = []
        except AttributeError:
            if not start_token:
                tokens.append(param_attr(p.replace(',', '').strip()))
            else:
                sub_list.append(p.replace(',', '').strip())

    possible_sub_type = possible_sub_type if possible_sub_type else type_of[0]
    return possible_types[possible_sub_type](tokens)


def param_attr(attr: str):
    """
    :return: builtin class or typing instance
    """
    try:
        return getattr(typing, attr)
    except AttributeError:
        return getattr(builtins, attr)


def recursive_isinstance(obj: typing.Any, typ: typing.Any, *, length_matches: bool = False) -> bool:
    try:
        _isinstance = all(recursive_isinstance(o, t, length_matches=length_matches) for o, t in zip(obj, typ))
    except TypeError:
        _isinstance = isinstance(obj, typ)
    if length_matches:
        return _isinstance and length_is_matching(obj, typ)
    return _isinstance


def length_is_matching(obj: typing.Any, value: typing.Any):
    try:
        # resolve problem with strings because they are iterable too
        obj_length = len(obj) if not isinstance(obj, str) else len(obj.split(' '))
        return obj_length == len(value)
    except TypeError:
        return True


def get_container_types(ttype_of: str) -> typing.Union[None, tuple]:
    pattern = r'([\(\[]\w+)' if 'or' not in ttype_of else OR_PATTERN
    pattern = pattern if ', ' not in ttype_of else COMMA_PATTERN
    sub_pattern = re.findall(pattern, ttype_of)
    sub_pattern = sub_pattern if 'or' not in ttype_of else sub_pattern[0]
    sub_pattern = sub_pattern if ', ' not in ttype_of else sub_pattern[0]
    try:
        container_types = tuple(param_attr(re.sub(REMOVE_PATTERN, '', t).strip()) for t in sub_pattern if t != 'or')
    except TypeError:
        container_types = None
    return container_types


def get_or_types(ttype: str) -> list:
    if ' or ' in ttype:
        return [t for t in re.findall(r'(\w+)\W+(or)\W+(\w+)', ttype)[0] if t != 'or']
    else:
        return re.findall(r'\w{2,}', ttype)


def is_tuple(arg, type_of: str):
    container_types = get_container_types(type_of)
    sub_types = all(isinstance(a, container_types) for a in arg) and len(arg) == len(
        container_types) if container_types else True
    return isinstance(arg, tuple) and sub_types


def is_list(arg, type_of: str):
    container_types = get_container_types(type_of)
    sub_types = all(isinstance(a, container_types) for a in arg) if container_types else True
    return isinstance(arg, list) and sub_types


def is_dict(arg, type_of: str):
    container_types = get_container_types(type_of)
    sub_types = all(isinstance(k, container_types[0]) for k in arg.keys()) and all(
        isinstance(v, container_types[1]) for v in arg.values()) if container_types else True
    return isinstance(arg, dict) and sub_types


def is_set(arg, type_of: str):
    return isinstance(arg, set)


def is_function_or_method_type(arg, type_of):
    type_dict = {
        'F': isinstance(arg, FunctionType),
        'M': isinstance(arg, MethodType)
    }
    return type_dict[type_of[0]]


options = {
    'tuple': is_tuple,
    'list': is_list,
    'set': is_set,
    'dict': is_dict
}


def check_doc_str_type(arg, type_of):
    check_result = True
    if type_of is not None:
        try:
            return options[re.split(REMOVE_PATTERN, type_of)[0]](arg, type_of)
        except KeyError:
            if len(re.findall(FM_PATTERN, type_of)) == 1:
                return is_function_or_method_type(arg, type_of)
            try:
                return isinstance(arg, tuple(map(param_attr, get_or_types(type_of))))
            except AttributeError:
                return arg.__class__.__name__ == type_of
    return check_result


def is_type_info(docstring_line: str) -> bool:
    allowed = [':type', ':vartype']
    return any(docstring_line.startswith(a) for a in allowed)


def is_param_info(docstring_line: str) -> bool:
    allowed = [':param', ':parameter', ':arg', ':argument', ':key', ':keyword']
    return any(docstring_line.startswith(a) for a in allowed)


def extract_docstring_param_types(func) -> dict:
    """
    extract the types to the defined parameters from the docstring
    """
    param = [separate_param_type(string)[0].split() for string in inspect.getdoc(func).split('\n') if
             is_param_info(string)]
    docstring = [separate_param_type(string) for string in inspect.getdoc(func).split('\n') if is_type_info(string)]
    docstring += [list(reversed(p)) for p in param if len(p) > 1]
    _docstring_types = {ds[0]: ds[1] for ds in docstring}
    # there is mismatch when user will mix type and param to bring them in the right order
    # we will look at the signature and recreate the previous dict to the final one
    return {k: _docstring_types.get(k, k) for k in inspect.signature(func).parameters.keys()}


def match_docstring(_func=None, *, excep_raise: Exception = TypeMisMatch, cache_size=0):
    cached_set = None if cache_size == 0 else CachedSet(cache_size)

    def wrapper(func):
        docstring_types = extract_docstring_param_types(func)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            if cached_set is not None:
                # check if func with args and kwargs was checked once before with positive result
                cached_key = (func, args.__str__(), kwargs.__str__())
                if cached_key in cached_set:
                    return func(*args, **kwargs)

            if 'self' in docstring_types:
                docstring_types['self'] = args[0].__class__.__name__
            if 'cls' in docstring_types:
                docstring_types['cls'] = args[0].__name__
            # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
            failed_params = tuple(
                arg_name for arg, arg_name in zip(args, docstring_types) if not check_doc_str_type(arg,
                                                                                                   docstring_types.get(
                                                                                                       arg_name))
            )
            failed_params += tuple(
                kwarg_name for kwarg_name, kwarg in kwargs.items() if not check_doc_str_type(kwarg,
                                                                                             docstring_types.get(
                                                                                                 kwarg_name)))
            if failed_params:
                msg = f'Incorrect parameters: {", ".join(f"{name}: {docstring_types[name]}" for name in failed_params)}'
                if excep_raise is not None:
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


class match_class_docstring(match_class_typing):
    match_func = match_docstring
