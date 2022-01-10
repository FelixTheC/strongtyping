#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 16.04.21
@author: eisenmenger
"""
from __future__ import annotations

import inspect
import sys
from functools import lru_cache
from pprint import pprint
from string import punctuation

RECURSION_LIMIT = 5


def find_type_in_stack_trace(obj_name, func_globals, recursion_limit=RECURSION_LIMIT, level=0):
    if not isinstance(obj_name, (str, bytes)):
        return obj_name
    if recursion_limit == 0:
        try:
            return eval(obj_name, func_globals)
        except NameError:
            return obj_name

    stack_trace = getattr(sys, "_getframe")(level)
    if obj_name in stack_trace.f_locals:
        if obj_name in stack_trace.f_globals:
            return stack_trace.f_globals[obj_name]
        return stack_trace.f_locals[obj_name]
    else:
        return find_type_in_stack_trace(obj_name, func_globals, recursion_limit - 1, level + 1)


def resolve_class_resolution(annotation_dict: dict) -> dict:
    """
    This will solve:
        class Dummy:
            attr = 100

            def foo(self, val: Union[int, float], other: 'Dummy'):
                return val * other.attr
    """
    final_dict = {
        key: annotation_dict[val] if val in annotation_dict else val
        for key, val in annotation_dict.items()
    }
    return final_dict


@lru_cache(1024)
def get_type_hints(func):
    """
    the values inside of the annotations are, since Python-3.10, strings
    this function will check up the stacktrace until a certain level to create the real object.
    """
    arg_names = [name for name in inspect.signature(func).parameters]
    _annotations = func.__annotations__
    addon_dict = {}
    if inspect.ismethod(func):
        for k, v in _annotations.items():
            if v[0] in list(punctuation):
                _annotations[k] = v[1:-1]
                addon_dict[v[1:-1]] = "cls_"
    _annotations = _annotations | addon_dict
    _annotations = {
        k: find_type_in_stack_trace(v, func.__globals__) for k, v in _annotations.items()
    }
    return arg_names, resolve_class_resolution(_annotations)


@lru_cache(1024)
def get_type_hint(obj_name, recursion_limit=RECURSION_LIMIT, level=0):
    stack_trace = sys._getframe(level)
    obj = None
    while True:
        try:
            obj = eval(obj_name, stack_trace.f_globals, stack_trace.f_locals)
        except NameError:
            level += 1
            stack_trace = sys._getframe(level)
        else:
            break
        finally:
            if recursion_limit == 0:
                break
            recursion_limit -= 1
    return obj
