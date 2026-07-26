from collections import namedtuple
from keyword import iskeyword
from typing import Any, Dict, List, Optional, Tuple, Union

from strongtyping.docstring_typing import check_doc_str_type
from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import check_type

use_match_typing: Dict[bool, Any] = {True: check_type, False: check_doc_str_type}


@match_typing
def typed_namedtuple(
    typename: str,
    field_names: Union[List[str], str, List[Tuple[str, object]]],
    *,
    rename: bool = False,
    defaults: Optional[Union[list[Any], tuple[Any, ...]]] = None,
    module: Optional[str] = None,
) -> type:
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

    _field_types: Dict[str, Any] = {}

    def rename_fields() -> Dict[str, Any]:
        knowing: set[str] = set()
        updated_dict: Dict[str, Any] = {}
        for index, name in enumerate(_field_types.keys()):
            if not name.isidentifier() or iskeyword(name) or name.startswith("_"):
                updated_dict[f"_{index}"] = _field_types[name]
            else:
                updated_dict[name] = _field_types[name]
            knowing.add(name)
        return updated_dict

    def validate_field_names() -> None:
        seen = set()
        for name in _field_types.keys():
            if name.startswith("_"):
                raise ValueError(f"Field names cannot start with an underscore: {name!r}")

            if not name.isidentifier():
                raise ValueError(f"Type names and field names must be valid identifiers: {name!r}")
            if iskeyword(name):
                raise ValueError(f"Type names and field names cannot be a keyword: {name!r}")

            if name in seen:
                raise ValueError(f"Encountered duplicate field name: {name!r}")
            seen.add(name)

    def contains_typing(f_name: Union[str, tuple[Any, ...]]) -> bool:
        return ":" in f_name or isinstance(f_name, tuple)

    def check_type_namedtuple(_value_dict: dict[str, Any], use_mt: bool = False) -> None:
        _use_match_typing: Any = use_match_typing
        failed_params = tuple(
            f"{k}: {v}"
            for k, v in _value_dict.items()
            if not _use_match_typing[use_mt](v, _field_types[k])
        )
        if failed_params:
            msg = f"Incorrect parameters: {failed_params}"
            raise TypeError(msg)

    _fields = (
        [name.strip() for name in field_names.split(",")]
        if isinstance(field_names, (str,))
        else field_names
    )

    typing_true, typing_false = (
        all(contains_typing(fn) for fn in _fields),
        not all(contains_typing(fn) for fn in _fields),
    )

    if typing_false and not typing_true:
        if any(contains_typing(fn) for fn in _fields):
            raise TypeError("No mixing of typing and not typing supported")
        _field_names: Any = _fields
        return namedtuple(typename, _field_names, rename=rename, defaults=defaults, module=module)
    else:
        try:
            _field_types = {k: v for k, v in map(lambda x: x.split(":"), _fields)}
            _use_match = False
        except (AttributeError, ValueError):
            _field_types = {k: v for k, v in _fields}  # type: ignore
            _use_match = True

        if rename is True:
            _field_types = rename_fields()
        else:
            validate_field_names()

        def _values_to_add(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            _a = {k: v for k, v in zip(_field_types.keys(), args)}
            _b = {k: v for k, v in kwargs.items() if k in _field_types}
            return {**_a, **_b}

        def _values_with_defaults() -> Dict[str, Any]:
            if defaults is not None:
                if len(_field_types) != len(defaults):
                    raise TypeError("Default values must match with field names")
                _defaults = {k: v for k, v in zip(_field_types.keys(), defaults)}
                check_type_namedtuple(_defaults, _use_match)
                return _defaults
            else:
                raise TypeError(f"Initialise {typename} with values or add defaults")

        def __new__(cls: type, *args: Any, **kwargs: Any) -> Any:
            _values = _values_to_add(*args, **kwargs)
            if not _values:
                _values = _values_with_defaults()
            if _values and defaults is not None:
                _values = _values_with_defaults()
                _values.update(**_values_to_add(*args, **kwargs))
            check_type_namedtuple(_values, _use_match)
            new_tuple: Any = tuple.__new__(cls, _values.values())
            for k, v in _values.items():
                setattr(new_tuple, k, v)
            return new_tuple

        __new__.__doc__ = f"Create new instance of {typename}({_field_types.keys()})"

        if defaults is not None:
            __new__.__defaults__ = tuple(defaults)
            _field_defaults = _values_with_defaults()
        else:
            _field_defaults = None

        def _asdict(self: Any) -> Dict[str, Any]:
            return {k: v for k, v in zip(_field_types.keys(), self)}

        def _replace(self: Any, **kwargs: Any) -> Any:
            new_val = self._asdict()
            not_allowed = [k for k in kwargs.keys() if k not in _field_types]
            if not_allowed:
                raise ValueError(f"Got unexpected field names: {not_allowed!r}")
            new_val.update(**kwargs)
            return self.__new__(self.__class__, **new_val)

        _replace.__doc__ = (
            f"Return a new {typename} object replacing specified fields with new values"
        )

        repr_fmt = "(" + ", ".join(f"{name}=%r" for name in _field_types.keys()) + ")"

        def __repr__(self: Any) -> str:
            """Return a nicely formatted representation string"""
            _repr: str = self.__class__.__name__ + repr_fmt % self
            return _repr

        def __getnewargs__(self: Any) -> Tuple[Any, ...]:
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
            "__doc__": f"{typename}({', '.join(_field_types.keys())})\n{class_doc}",
            "_field_defaults": _field_defaults,
        }

        if _use_match:
            namespace["__annotations__"] = _field_types
        return type(typename, (tuple,), namespace)
