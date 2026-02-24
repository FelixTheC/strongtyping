#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 30.05.21
@author: felix
"""
import inspect
import json
import weakref
from functools import partial
from typing import Any, _GenericAlias, _SpecialForm, _type_repr


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


class FrozenType:
    __slots__ = ("required_type", "stored_value", "weakref")

    def __init__(self, required_type, stored_value=None):
        self.weakref = weakref.WeakKeyDictionary()
        self.required_type = required_type
        self.stored_value = stored_value

    def __get__(self, instance=None, owner=None):
        return self.weakref.get(instance, (None, self.stored_value))[1]

    def __set__(self, instance=None, value=None):
        if isinstance(value, tuple) and isinstance(value[0], FrozenType):
            required_type, stored_value = self.weakref.get(
                instance, (self.required_type, self.stored_value)
            )
            new_required_type, original_type = value[1], required_type
            try:
                updated_stored_value = new_required_type(stored_value)
            except TypeError:
                raise TypeError(f"Cannot cast {self.required_type} to {value[1]}")
            else:
                self.required_type = new_required_type
                self.stored_value = updated_stored_value
                self.weakref[value[-1]] = (new_required_type, updated_stored_value)
        else:
            if not isinstance(value, self.weakref.get(instance, (self.required_type,))[0]):
                self.error_msg(value)
            else:
                self.weakref[instance] = (self.required_type, value)

    def __repr__(self):
        return repr(self.required_type)

    def __str__(self):
        return str(self.stored_value)

    def __doc__(self):
        return self.required_type.__doc__

    @classmethod
    def cast(cls, instance, origin, new):
        """
        change the type explicit not implicit by accident
        """
        try:
            new(origin)
        except TypeError:
            raise TypeError(f"Cannot cast {type(origin)} to {new}")
        return FrozenType(FrozenType), new, instance

    def error_msg(self, value: Any, attribute_name: str = "This") -> Exception:
        raise TypeError(
            f"`{attribute_name}` is a final type. "
            f"\n\tYou cannot assign {type(value)} to {self.required_type}"
        )
