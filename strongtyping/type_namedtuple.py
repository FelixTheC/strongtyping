#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 13.07.20
@author: felix
"""
from collections import namedtuple
from keyword import iskeyword
from typing import Any, List, Tuple, Union

from strongtyping.docstring_typing import check_doc_str_type
from strongtyping.strong_typing import check_type, match_typing

use_match_typing = {True: check_type, False: check_doc_str_type}


@match_typing
def typed_namedtuple(
    typename: str,
    field_names: Union[List[str], str, List[Tuple[str, Any]]],
    *,
    rename: bool = False,
    defaults: Union[list, tuple] = None,
    module: str = None,
):
    # I could have just copied everything from namedtuple, but then I would have no learning effect
    """
    :param typename: the name of the new class same as in the original namedtuple
    :param field_names: as in the original field_names can be written as string or list
    to use typing write:
        'foo:int,bar:str,foobar:list
            or
        ['foo:int', 'bar:str', 'foobar:list']
            if no "typing" is inside of the field_names it will return the original namedtuple
    :param rename: same as in the original namedtuple
    :param defaults: the default values to use when instantiate, must match field_names length
    :param module: the module of the class same as in the original namedtuple
    :return:
    """

    def rename_fields():
        knowing = set()
        updated_dict = {}
        for index, name in enumerate(_field_types.keys()):
            if not name.isidentifier() or iskeyword(name) or name.startswith("_"):
                updated_dict[f"_{index}"] = _field_types[name]
            else:
                updated_dict[name] = _field_types[name]
            knowing.update(name)
        return updated_dict

    def validate_field_names():
        seen = set()
        for name in _field_types.keys():
            if name.startswith("_"):
                raise ValueError(f"Field names cannot start with an underscore: {name!r}")

            if not name.isidentifier():
                raise ValueError(
                    "Type names and field names must be valid " f"identifiers: {name!r}"
                )
            if iskeyword(name):
                raise ValueError("Type names and field names cannot be a " f"keyword: {name!r}")

            if name in seen:
                raise ValueError(f"Encountered duplicate field name: {name!r}")
            seen.add(name)

    def contains_typing(f_name: Union[str, tuple]) -> bool:
        return ":" in f_name or isinstance(f_name, tuple)

    def check_type(_value_dict: dict, use_mt: bool = False):
        failed_params = tuple(
            f"{k}: {v}"
            for k, v in _value_dict.items()
            if not use_match_typing[use_mt](v, _field_types[k])
        )
        if failed_params:
            msg = f"Incorrect parameters: {failed_params}"
            raise TypeError(msg)

    _fields = (
        [name.strip() for name in field_names.split(",")]
        if isinstance(field_names, (str,))
        else field_names
    )

    typing_true, typing_false = all(contains_typing(fn) for fn in _fields), not all(
        contains_typing(fn) for fn in _fields
    )

    if typing_false and not typing_true:
        if any(contains_typing(fn) for fn in _fields):
            raise TypeError("No mixing of typing and not typing supported")
        return namedtuple(typename, field_names, rename=rename, defaults=defaults, module=module)
    else:
        try:
            _field_types = {k: v for k, v in map(lambda x: x.split(":"), _fields)}
            _use_match = False
        except AttributeError:
            _field_types = {k: v for k, v in _fields}
            _use_match = True

        if rename is True:
            _field_types = rename_fields()
        else:
            validate_field_names()

        def _values_to_add(*args, **kwargs):
            _a = {k: v for k, v in zip(_field_types.keys(), args)}
            _b = {k: v for k, v in kwargs.items() if k in _field_types}
            return {**_a, **_b}

        def _values_with_defaults():
            if defaults is not None:
                if len(_field_types) != len(defaults):
                    raise TypeError("Default values must match with field names")
                _defaults = {k: v for k, v in zip(_field_types.keys(), defaults)}
                check_type(_defaults, _use_match)
                return _defaults
            else:
                raise TypeError(f"Initialise {typename} with values or add defaults")

        def __new__(cls, *args, **kwargs):
            _values = _values_to_add(*args, **kwargs)
            if not _values:
                _values = _values_with_defaults()
            if _values and defaults is not None:
                _values = _values_with_defaults()
                _values.update(**_values_to_add(*args, **kwargs))
            check_type(_values, _use_match)
            new_tuple = tuple.__new__(cls, _values.values())
            [setattr(new_tuple, k, v) for k, v in _values.items()]
            return new_tuple

        __new__.__doc__ = f"Create new instance of {typename}({_field_types.keys()})"

        if defaults is not None:
            __new__.__defaults__ = tuple(defaults)
            _field_defaults = _values_with_defaults()
        else:
            _field_defaults = None

        def _asdict(self):
            return {k: v for k, v in zip(_field_types.keys(), self)}

        def _replace(self, **kwargs):
            new_val = self._asdict()
            not_allowed = [k for k in kwargs.keys() if k not in self._field_types]
            if not_allowed:
                raise ValueError(f"Got unexpected field names: {not_allowed!r}")
            new_val.update(**kwargs)
            return self.__new__(self.__class__, **new_val)

        _replace.__doc__ = (
            f"Return a new {typename} object replacing specified fields with new values"
        )

        repr_fmt = "(" + ", ".join(f"{name}=%r" for name in _field_types.keys()) + ")"

        def __repr__(self):
            """Return a nicely formatted representation string"""
            return self.__class__.__name__ + repr_fmt % self

        def __getnewargs__(self):
            """Return self as a plain tuple.  Used by copy and pickle."""
            return tuple(self)

        class_doc = "\n".join([f":type {k}: {val}" for k, val in _field_types.items()])

        namespace = {
            "__new__": __new__,
            "__module__": module if module is not None else __name__,
            "_field_types": _field_types,
            "_asdict": _asdict,
            "_replace": _replace,
            "__getnewargs__": __getnewargs__,
            "__repr__": __repr__,
            "__doc__": f'{typename}({", ".join(_field_types.keys())})\n{class_doc}',
            "_field_defaults": _field_defaults,
        }

        if _use_match:
            namespace["__annotations__"] = _field_types
        return type(typename, (tuple,), namespace)
