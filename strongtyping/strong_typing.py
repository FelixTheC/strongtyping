#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 28.04.20
@author: felix
"""
import inspect
from functools import wraps
import warnings
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing_utils import TypeMisMatch
from strongtyping.strong_typing_utils import check_type

from strongtyping._utils import action
from strongtyping._utils import _get_new
from strongtyping._utils import _severity_level
from strongtyping._utils import remove_subclass
from strongtyping.cached_set import CachedSet

F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')


def match_typing(_func: Optional[F] = None, *,
                 excep_raise: Type[Exception] = TypeMisMatch,
                 cache_size: int = 0,
                 subclass: bool = False,
                 severity: Union[str, SEVERITY_LEVEL] = 'env',
                 **kwargs: Dict[Any, Any]) -> Callable[..., Any]:

    cached_set = None if cache_size == 0 else CachedSet(cache_size)

    def wrapper(func: F) -> Callable[..., Any]:
        # needed in py 3.10
        # globals().update(func.__globals__)

        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__

        severity_level = _severity_level(severity)

        @wraps(func)
        def inner(*args: List[Any], **kwargs: Dict[Any, Any]) -> Callable[..., Any]:
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

        inner.__fe_strng_mtch__ = 0  # type: ignore
        return inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper


def match_class_typing(_cls: Optional[T] = None, *,
                       excep_raise: Type[Exception] = TypeError,
                       cache_size: int = 0,
                       severity: Union[str, SEVERITY_LEVEL] = 'env',
                       **kwargs: Dict[Any, Any]) -> Union[T, Callable[[T], T]]:

    def wrapper(cls: T) -> T:

        severity_level = _severity_level(severity)
        if severity_level > 0:
            cls.__new__ = _get_new(match_typing, excep_raise, cache_size, severity, **kwargs)  # type: ignore
            if hasattr(cls.__init__, '__annotations__'):   # type: ignore
                cls.__init__ = match_typing(cls.__init__)  # type: ignore
        return cls

    if _cls is not None:
        return wrapper(_cls)
    else:
        return wrapper


def getter(func: F) -> property:
    return action(func, 'getter', match_typing)


def setter(func: F) -> property:
    return action(func, 'setter', match_typing)


def getter_setter(func: F) -> property:
    return action(func, 'getter_setter', match_typing)
