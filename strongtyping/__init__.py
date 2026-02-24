#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

try:
    from strongtyping._c_impl import (
        dict_elements as _dict_elements,
        list_elements as _list_elements,
        set_elements as _set_elements,
        tuple_elements as _tuple_elements,
    )

    IS_EXT_INSTALLED = True
except ImportError:
    # Fallback to the pure Python implementation
    from strongtyping._py_impl import (
        checking_typing_dict as _dict_elements,
        checking_typing_list as _list_elements,
        checking_typing_set as _set_elements,
        checking_typing_tuple as _tuple_elements,
    )

    IS_EXT_INSTALLED = False
    logging.debug("Cython extension not found; using pure Python.")


def dict_elements(obj, type_obj, *args, **kwargs):
    return _dict_elements(obj, type_obj, *args, **kwargs)


def list_elements(obj, type_obj, *args, **kwargs):
    return _list_elements(obj, type_obj, *args, **kwargs)


def set_elements(obj, type_obj, *args, **kwargs):
    return _set_elements(obj, type_obj, *args, **kwargs)


def tuple_elements(obj, type_obj, *args, **kwargs):
    return _tuple_elements(obj, type_obj, *args, **kwargs)


__all__ = [
    "_utils",
    "strong_typing_utils",
    "strong_typing",
    "docstring_typing",
    "cached_set",
    "cached_dict",
    "type_namedtuple",
    "helpers",
    "_py_impl",
    "_c_impl",
]
