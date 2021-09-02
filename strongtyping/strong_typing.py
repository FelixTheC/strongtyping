#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 28.04.20
@author: felix
"""
import functools
import inspect
import pprint
import warnings
from functools import wraps
from typing import Type

from strongtyping._utils import _severity_level, action, remove_subclass
from strongtyping.cached_set import CachedSet
from strongtyping.strong_typing_utils import (
    TypeMisMatch,
    check_type,
    checking_typing_typedict_values,
    default_return_queue,
    py_version,
)


def match_typing(
    _func=None,
    *,
    excep_raise: Type[Exception] = TypeMisMatch,
    subclass: bool = False,
    severity="env",
    **kwargs,
):
    cached_enabled: int = kwargs.get("cache_size", 1)
    cached_set = CachedSet(cached_enabled) if cached_enabled > 0 else None

    def wrapper(func):
        # needed in py 3.10
        # globals().update(func.__globals__)

        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__
        severity_level = _severity_level(severity)

        @wraps(func)
        def inner(*args, **kwargs):
            if arg_names and severity_level > 0:

                args = remove_subclass(args, subclass)
                if cached_set is not None and func.__name__ not in ("__init__",):
                    # check if func with args and kwargs was checked once before with positive result
                    cached_key = (func, args.__str__(), kwargs.__str__())
                    if cached_key in cached_set:
                        return func(*args, **kwargs)

                # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
                failed_params = tuple(
                    arg_name
                    for arg, arg_name in zip(args, arg_names)
                    if not check_type(arg, annotations.get(arg_name))
                )
                failed_params += tuple(
                    kwarg_name
                    for kwarg_name, kwarg in kwargs.items()
                    if not check_type(kwarg, annotations.get(kwarg_name))
                )

                if not default_return_queue.empty():
                    return default_return_queue.queue.pop()

                if failed_params:
                    annotated_values = {arg_name: arg for arg, arg_name in zip(args, arg_names)}
                    for kwarg_name, kwarg in kwargs.items():
                        annotated_values[kwarg_name] = kwarg

                    msg_list = "\nIncorrect parameter: ".join(
                        f"[{name}] `{pprint.pformat(annotated_values[name], width=20, depth=2)}`"
                        f"\n\trequired: {annotations[name]}"
                        for name in failed_params
                    )
                    msg = f"Incorrect parameter: {msg_list}"

                    if excep_raise is not None and severity_level == 1:
                        raise excep_raise(msg) from None
                    else:
                        warnings.warn(msg, RuntimeWarning)

                if cached_set is not None and func.__name__ not in ("__init__",):
                    cached_set.add(cached_key)
            return func(*args, **kwargs)

        inner.__fe_strng_mtch__ = 0
        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper


class match_class_typing:
    def __new__(cls, instance=None, *args, **kwargs):
        cls.cls = instance
        return super().__new__(cls)

    def __init__(self, cls=None, *args, **kwargs):
        self.excep_raise = kwargs.pop("excep_raise", TypeMisMatch)
        self.cache_size = kwargs.pop("cache_size", 1)
        self.severity = kwargs.pop("severity", "env")
        self.cls = cls

    def __getattr__(self, item):
        return getattr(self.cls, item)

    @staticmethod
    def __has_annotations__(obj):
        return hasattr(obj, "__annotations__")

    def __find_methods(self, cls):
        return [
            func
            for func in dir(cls)
            if callable(getattr(cls, func))
            and self.__has_annotations__(getattr(cls, func))
            and not hasattr(getattr(cls, func), "__fe_strng_mtch__")
            and not isinstance(getattr(cls, func), classmethod)
        ]

    def __add_decorator(self, cls):
        severity_level = _severity_level(self.severity)
        if severity_level > 0:
            for method in self.__find_methods(cls):
                try:
                    setattr(
                        cls,
                        method,
                        match_typing(
                            getattr(cls, method),
                            severity=self.severity,
                            cache_size=self.cache_size,
                            excep_raise=self.excep_raise,
                        ),
                    )
                except TypeError:
                    pass

    @property
    def is_typed_dict(self):
        if py_version < 9:
            return hasattr(self.cls, "__total__")
        if hasattr(self.cls, "__orig_bases__"):
            return any(obj.__name__ == "TypedDict" for obj in self.cls.__orig_bases__)

    def create_error_msg(self, args: dict):
        return (
            f"Incorrect parameter: `{pprint.pformat(args, width=20, depth=2)}`"
            f"\n\trequired: {self.__annotations__}"
        )

    def __call__(self, *args, **kwargs):
        if self.is_typed_dict:
            arguments = kwargs if kwargs else args[0]
            if not checking_typing_typedict_values(arguments, self.__annotations__, self.__total__):
                raise self.excep_raise(self.create_error_msg(arguments))
        if self.cls:
            if self.__has_annotations__(self.cls.__init__):
                self.cls.__init__ = match_typing(self.cls.__init__)
            cls = self.cls(*args, **kwargs)
            self.__add_decorator(cls)
        else:
            cls = args[0]
            self.__add_decorator(cls)
        return cls

    def __repr__(self):
        return repr(self.cls)

    def __str__(self):
        return str(self.cls)


def getter(func):
    return action(func, "getter", match_typing)


def setter(func):
    return action(func, "setter", match_typing)


def getter_setter(func):
    return action(func, "getter_setter", match_typing)


class FinalClass:
    def __new__(cls, instance=None, *args, **kwargs):
        if args:
            raise RuntimeError(
                f"`class {instance}` can not inherit from `class {args[0][0].__name__}`"
            )
        cls.cls = instance
        return super().__new__(cls)

    def __init__(self, cls=None, *args, **kwargs):
        self.cls = cls

    def __getattr__(self, item):
        return getattr(self.cls, item)

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)

    def __repr__(self):
        return repr(self.cls)

    def __str__(self):
        return str(self.cls)

    @property
    def __doc__(self):
        return self.cls.__doc__
