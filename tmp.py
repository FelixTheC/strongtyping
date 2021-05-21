#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 12.05.21
@author: eisenmenger
"""
from functools import wraps
from itertools import count
from typing import Union
import inspect

from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import TypeMisMatch, ValidType, _ValidType, \
    get_possible_types, get_origins


def getsource(object):
    """Return the text of the source code for an object.

    The argument may be a module, class, method, function, traceback, frame,
    or code object.  The source code is returned as a single string.  An
    OSError is raised if the source code cannot be retrieved."""
    lines, lnum = inspect.getsourcelines(object)
    return ''.join(lines[1:])


def docs_from_tying(func):

    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    annotations = func.__annotations__
    doc_infos = [f"Function: {func.__name__}", '-' * 30]
    for key, val in annotations.items():
        if key != 'return':
            doc_infos.append(f':param: {key}')
            doc_infos.append(f':type: {val}')
            if get_origins(val)[1] == 'ValidType':
                doc_infos.append(f':requirement: \n{getsource(get_possible_types(val)[1])}')

    if 'return' in annotations:
        doc_infos.append(f'\n:returns: {annotations["return"].__name__}')

    text = '\n'.join(doc_infos)
    inner.__doc__ = text
    return inner


def validate_input(val):
    if not (0 < val < 10000) or (hasattr(val, 'is_integer') and not val.is_integer()):
        # A float is an integer if the remainder is 0 like 10.0
        return False


def validate_str_input(val):
    return 10 < len(val) < 20


@match_typing
@docs_from_tying
def foo(val: ValidType[int, validate_input],
        val_2: ValidType[str, validate_str_input]) -> int:
    return val ** 2


# def test_valid_input():
#     for i in range(1, 10000):
#         assert foo(i) == i ** 2
#
#
# def test_invalid_input():
#     counter = count(start=1.01, step=.01)
#     for i in range(500):
#         try:
#             foo(next(counter))
#         except TypeMisMatch:
#             assert True
#         else:
#             raise AssertionError
#
#     for i in range(1, 10000):
#         try:
#             foo(i * -1)
#         except TypeMisMatch:
#             assert True
#         else:
#             raise AssertionError
#
#     for data in ("1", "foo", "bar"):
#         try:
#             foo(data)
#         except TypeMisMatch:
#             assert True
#         else:
#             raise AssertionError


if __name__ == '__main__':
    print(foo.__doc__)
