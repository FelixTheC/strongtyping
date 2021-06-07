#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 30.05.21
@author: felix
"""
import inspect
import json
from functools import partial
from typing import _GenericAlias, _SpecialForm, _type_repr

from strongtyping.strong_typing_utils import py_version


class _Validator(_GenericAlias, _root=True):  # type: ignore
    _name = "Validator"

    def __getitem__(self, item):
        return super().__getitem__(item)

    def __hash__(self):
        if len(self.__args__) > 2:
            return hash(frozenset([self.__args__[:-1], json.dumps(self.__args__[-1])]))
        return hash(frozenset(self.__args__))

    def __repr__(self):
        args = self.__args__
        validator = args[1].func if isinstance(args[1], partial) else args[1]
        func_name = validator.__name__
        validation_function_file = inspect.getfile(validator)
        validation_body, validation_line = inspect.getsourcelines(validator)
        validation_lines = validation_line + len(validation_body)
        func_info = (
            f"{func_name}(<{validation_function_file}>, "
            f"lines={validation_line}-{validation_lines})"
        )
        return f"strong_typing_utils.Validator[{_type_repr(args[0])}, {func_info}]"


class _IterValidator(_GenericAlias, _root=True):  # type: ignore
    _name = "IterValidator"

    def __getitem__(self, item):
        return super().__getitem__(item)

    def __hash__(self):
        if len(self.__args__) > 2:
            return hash(frozenset([self.__args__[:-1], json.dumps(self.__args__[-1])]))
        return hash(frozenset(self.__args__))

    def __repr__(self):
        args = self.__args__
        validator = args[1].func if isinstance(args[1], partial) else args[1]
        func_name = validator.__name__
        validation_function_file = inspect.getfile(validator)
        validation_body, validation_line = inspect.getsourcelines(validator)
        validation_lines = validation_line + len(validation_body)
        func_info = (
            f"{func_name}(<{validation_function_file}>, "
            f"lines={validation_line}-{validation_lines})"
        )
        return f"strong_typing_utils.IterValidator[{_type_repr(args[0])}, {func_info}]"


if py_version >= 9:

    @_SpecialForm  # type: ignore
    def Validator(self, parameters, *args, **kwargs):
        if isinstance(parameters, _GenericAlias):
            raise TypeError("Validator needs min 2 values. Validator[type, function]")
        if not parameters:
            raise TypeError("Cannot take a Validator of no type/function.")
        if len(parameters) > 3:
            raise TypeError("Validator takes max 3 values.")
        if not inspect.isfunction(parameters[1]) and not isinstance(parameters[1], partial):
            raise TypeError("Validator[..., arg]: arg should be a function.")
        return _Validator(self, parameters)

    @_SpecialForm  # type: ignore
    def IterValidator(self, parameters, *args, **kwargs):
        if isinstance(parameters, _GenericAlias):
            raise TypeError("Validator needs min 2 values. Validator[type, function]")
        if not parameters:
            raise TypeError("Cannot take a Validator of no type/function.")
        if len(parameters) > 3:
            raise TypeError("Validator takes max 3 values.")
        if not inspect.isfunction(parameters[1]) and not isinstance(parameters[1], partial):
            raise TypeError("Validator[..., arg]: arg should be a function.")
        return _IterValidator(self, parameters)


else:
    from typing import KT, VT, _alias, _GenericAlias, _type_repr  # type: ignore

    Validator = _alias(_Validator, (KT, VT), inst=False)
    IterValidator = _alias(_IterValidator, (KT, VT), inst=False)
