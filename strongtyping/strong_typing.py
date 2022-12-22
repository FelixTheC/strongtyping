import inspect
import pprint
import warnings
from functools import wraps
from typing import Type, get_args, get_origin

try:
    from typing_extensions import NotRequired, Required
except ImportError:
    NotRequired = object()
    Required = object()


from strongtyping._utils import _severity_level, action, remove_subclass
from strongtyping.cached_set import CachedSet
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing_utils import (
    TypeMisMatch,
    check_type,
    checking_typing_typedict_values,
    default_return_queue,
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
    check_duck_typing = kwargs.get("allow_duck_typing", False)

    def wrapper(func):
        # needed in py 3.10
        # globals().update(func.__globals__)

        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__
        severity_level = _severity_level(severity)

        @wraps(func)
        def inner(*args, **kwargs):
            if arg_names and severity_level > SEVERITY_LEVEL.DISABLED.value:

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
                    if not check_type(
                        arg,
                        annotations.get(arg_name),
                        mro=False,
                        check_duck_typing=check_duck_typing,
                    )
                )
                failed_params += tuple(
                    kwarg_name
                    for kwarg_name, kwarg in kwargs.items()
                    if not check_type(
                        kwarg,
                        annotations.get(kwarg_name),
                        mro=False,
                        check_duck_typing=check_duck_typing,
                    )
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

                    if excep_raise is not None and severity_level == SEVERITY_LEVEL.ENABLED.value:
                        raise excep_raise(
                            msg, failed_params, annotated_values, annotations
                        ) from None
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


def add_required_methods_to_class(cls, inst):
    for method in ("__instancecheck__",):
        try:
            setattr(cls, method, getattr(inst, method))
        except AttributeError:
            continue


class MatchTypedDict:
    def __new__(cls, instance=None, *args, **kwargs):
        cls.cls = instance
        add_required_methods_to_class(cls, instance)
        return super().__new__(cls)

    def __init__(self, cls=None, *args, **kwargs):
        self.excep_raise = kwargs.pop("excep_raise", TypeMisMatch)
        self.cache_size = kwargs.pop("cache_size", 1)
        self.severity = kwargs.pop("severity", "env")
        self.cls = cls

    def __getattr__(self, item):
        return getattr(self.cls, item)

    @property
    def is_typed_dict(self):
        if hasattr(self.cls, "__orig_bases__"):
            return any(obj.__name__ == "TypedDict" for obj in self.cls.__orig_bases__)
        try:
            return self.cls.__class__.__name__ == "_TypedDictMeta"
        except AttributeError:
            pass

    def create_error_msg(self, args: dict):
        return (
            f"Incorrect parameter: `{pprint.pformat(args, width=20, depth=2)}`"
            f"\n\trequired: {self.__annotations__}"
        )

    def _no_required_inside(self, val):
        if get_origin(val) is Required:
            return False
        try:
            new_val = get_args(val)[0]
        except IndexError:
            return True
        else:
            return self._no_required_inside(new_val)

    def check_annotations(self):
        last_non_required = None
        for idx, val in enumerate(self.__annotations__.values()):
            if get_origin(val) is NotRequired:
                if idx == 0 and self.__total__:
                    raise TypeError("NotRequired cannot before required")
                if not self._no_required_inside(get_args(val)[0]):
                    return False
                last_non_required = idx
            else:
                if last_non_required is not None and last_non_required < idx:
                    raise TypeError("NotRequired cannot before required")
        return True

    def __call__(self, *args, **kwargs):
        if self.is_typed_dict:
            arguments = kwargs if kwargs else args[0]
            if not self.check_annotations():
                raise TypeError("A NotRequired field can not contain Required")
            if not checking_typing_typedict_values(arguments, self.__annotations__, self.__total__):
                raise self.excep_raise(self.create_error_msg(arguments))
        if self.cls:
            cls = self.cls(*args, **kwargs)
        else:
            cls = args[0]
        return cls


def match_class_typing(cls=None, **kwargs):
    excep_raise = kwargs.pop("excep_raise", TypeMisMatch)
    cache_size = kwargs.pop("cache_size", 1)
    severity = kwargs.pop("severity", "env")

    def __has_annotations__(obj):
        return hasattr(obj, "__annotations__")

    def __find_methods(_cls):
        return [
            func
            for func in dir(_cls)
            if callable(getattr(_cls, func))
            and __has_annotations__(getattr(_cls, func))
            and not hasattr(getattr(_cls, func), "__fe_strng_mtch__")
            and not isinstance(getattr(_cls, func), classmethod)
        ]

    def __add_decorator(_cls):
        severity_level = _severity_level(severity)
        if severity_level > SEVERITY_LEVEL.DISABLED.value:
            for method in __find_methods(_cls):
                try:
                    func = getattr(_cls, method)
                    is_static = "self" not in inspect.signature(func).parameters
                    setattr(
                        _cls,
                        method,
                        match_typing(
                            func,
                            severity=severity,
                            cache_size=cache_size,
                            excep_raise=excep_raise,
                            subclass=is_static,
                        ),
                    )
                except TypeError:
                    pass

    def wrapper(some_cls):
        def inner(*args, **cls_kwargs):
            __add_decorator(some_cls)
            return some_cls(*args, **cls_kwargs)

        inner._matches_class = True
        return inner

    if cls is not None:
        from typing import Type, _TypedDictMeta

        try:
            from typing_extensions import _TypedDictMeta as _TypedDictMetaExtension
        except ImportError:
            if isinstance(cls, _TypedDictMeta):
                return MatchTypedDict(cls)
        else:
            if isinstance(cls, _TypedDictMeta) or isinstance(cls, _TypedDictMetaExtension):
                return MatchTypedDict(cls)

        __add_decorator(cls)
        cls._matches_class = True
        return cls
    else:
        return wrapper


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
