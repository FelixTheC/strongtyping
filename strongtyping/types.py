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
from itertools import zip_longest
from typing import Any, _GenericAlias, _SpecialForm, _type_repr, _BaseGenericAlias, _alias, KT, VT  # type: ignore

from strongtyping.strong_typing_utils import get_origins, get_possible_types

from strongtyping._utils import ORIGINAL_DUCK_TYPES


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


def _is_allowed_duck_type(arg, other):
    if arg == other:
        return True

    if arg in ORIGINAL_DUCK_TYPES:
        return arg in ORIGINAL_DUCK_TYPES[other]

    arg_mros = set(arg.__mro__[:-1])  # to exclude `object`

    required_mros = set(other.__mro__[:-1])
    return arg_mros.issuperset(required_mros)


def _check_typing_type(arg_typ, other_typ, *args, **kwargs):
    arg_origins = get_origins(arg_typ)
    other_origins = get_origins(other_typ)
    if arg_origins != other_origins:
        possible_args = get_possible_types(arg_typ) or (arg_typ,)
        possible_other = get_possible_types(other_typ) or (other_typ,)

        if 'Optional' in arg_origins or 'Optional' in other_origins:
            for arg, other in zip_longest(possible_args, possible_other):
                if arg is not None and other is not None:
                    if arg is not other and other in ORIGINAL_DUCK_TYPES:
                        check = other in ORIGINAL_DUCK_TYPES[arg]
                        if not check:
                            break
                    else:
                        check = arg is other
                        if not check:
                            break

        sub_arg = get_possible_types(arg_typ)
        sub_other = get_possible_types(other_typ)

        if hasattr(arg_typ, "__origin__") and hasattr(other_typ, "__origin__"):
            if not issubclass(arg_typ.__origin__, other_typ.__origin__):
                return False

        if sub_arg is not None and sub_other is not None:
            check = any(_is_allowed_duck_type(arg, other)
                        for arg, other in zip_longest(sub_arg, sub_other))

        elif sub_arg is None and sub_other is not None:
            check = any(_is_allowed_duck_type(arg_typ, other)
                        for other in sub_other)

        elif sub_arg is not None and sub_other is None:
            check = any(_is_allowed_duck_type(arg, other_typ)
                        for arg in sub_arg)
        else:
            check = _is_allowed_duck_type(arg_typ, other_typ)

    else:
        check = True
        possible_args = get_possible_types(arg_typ) or (arg_typ,)
        possible_other = get_possible_types(other_typ) or (other_typ,)
        for arg, other in zip_longest(possible_args, possible_other):
            try:
                check = issubclass(arg, other)
            except TypeError:
                try:
                    sub_arg = get_possible_types(arg)[0]
                except TypeError:
                    sub_arg = arg

                try:
                    sub_other = get_possible_types(other)[0]
                except TypeError:
                    sub_other = other

                check = _check_typing_type(sub_arg, sub_other)
                if not check:
                    break
            else:
                if not check:
                    break
    return check


class _Constant(_GenericAlias, _root=True):  # type: ignore
    _name = "Constant"

    def __getitem__(self, item):
        return super().__getitem__(item)

    def __hash__(self):
        if len(self.__args__) > 2:
            return hash(frozenset([self.__args__[:-1], json.dumps(self.__args__[-1])]))
        return hash(frozenset(self.__args__))

    def __eq__(self, other):
        return all(_check_typing_type(val, other_val)
                   for val, other_val in zip(self.__args__, other.__args__)
                   )

    def __repr__(self):
        return f"Constant[{_type_repr(self.__args__[0])}]"


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


@_SpecialForm  # type: ignore
def Constant(self, parameters):
    return _Constant(self, parameters)



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


class Entity:

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__class__.__annotations__!r})"

    def __init_subclass__(cls, **kwargs):
        if cls.__mro__[1] == Entity:
            return cls
        else:
            sub_cls = cls.__mro__[0]
            for parent in cls.__mro__[1:]:
                if parent.__name__ == Entity.__name__:
                    break
                parent_annotations = parent.__annotations__
                for key, val in sub_cls.__annotations__.items():
                    if parent_val := parent_annotations.get(key):
                        if val != parent_val:
                            raise AttributeError(f"`{sub_cls.__name__}.{val}` is not comparable with "
                                                 f"derived `{parent.__name__}.{parent_val!r}`")
        return cls

