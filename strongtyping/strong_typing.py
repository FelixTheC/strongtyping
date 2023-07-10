import copy
import inspect
import pprint
import warnings
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    NotRequired,
    Optional,
    ParamSpec,
    Required,
    Type,
    TypeVar,
    get_args,
    get_origin,
)

from strongtyping._utils import _get_severity_level, _severity_level, action, remove_subclass
from strongtyping.cached_set import CachedSet
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing_utils import (
    TypeMisMatch,
    check_type,
    checking_typing_typedict_values,
    default_return_queue,
)

P = ParamSpec("P")
FuncT = TypeVar("FuncT", bound=Callable[..., Any])
T = TypeVar("T")


# CACHE_IGNORE_CLASS_FUNCTIONS = ("__init__", "__str__", "__repr__")
CACHE_IGNORE_CLASS_FUNCTIONS = ("__init__",)


def match_typing(
    _func: FuncT,
    *,
    excep_raise: dict[Any, Any] | type[TypeMisMatch] = TypeMisMatch,
    subclass: bool = False,
    severity: SEVERITY_LEVEL | Literal["env"] = "env",
    **kwargs: Any,
) -> FuncT | Any:
    cached_enabled: int = kwargs.get("cache_size", 1)  # type: ignore
    cached_set = CachedSet(cached_enabled) if cached_enabled > 0 else None
    check_duck_typing = kwargs.get("allow_duck_typing", False)

    def wrapper(func: FuncT | T) -> Any:
        # needed in py 3.10
        # globals().update(func.__globals__)

        arg_names = [name for name in inspect.signature(func).parameters]  # type: ignore
        annotations = func.__annotations__
        severity_level = _severity_level(severity)

        @wraps(func)  # type: ignore
        def inner(*args, **kwargs):
            if arg_names and severity_level > SEVERITY_LEVEL.DISABLED.value:
                args = remove_subclass(args, subclass)

                if cached_set is not None and func.__name__ not in CACHE_IGNORE_CLASS_FUNCTIONS:
                    # check if func with args and kwargs was checked once before with positive result
                    arg_vals = args.__str__() if args else None
                    kwarg_vals = kwargs.__str__() if args else None
                    cached_key = (func, arg_vals, kwarg_vals)

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

                if cached_set is not None and func.__name__ not in CACHE_IGNORE_CLASS_FUNCTIONS:
                    cached_set.add(cached_key)
            return func(*args, **kwargs)

        inner.__fe_strng_mtch__ = 0  # type: ignore
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
    def __new__(cls, instance=None, *args, **kwargs) -> "MatchTypedDict":
        cls.cls = instance
        add_required_methods_to_class(cls, instance)
        return super().__new__(cls)

    def __init__(self, cls=None, *args, **kwargs) -> None:
        self.excep_raise = kwargs.pop("excep_raise", TypeMisMatch)
        self.cache_size = kwargs.pop("cache_size", 1)
        self.severity = kwargs.pop("severity", "env")
        self.cls = cls

    def __getattr__(self, item):
        return getattr(self.cls, item)

    @property
    def is_typed_dict(self) -> Optional[bool]:
        if hasattr(self.cls, "__orig_bases__"):
            return any(obj.__name__ == "TypedDict" for obj in self.cls.__orig_bases__)
        try:
            return self.cls.__class__.__name__ == "_TypedDictMeta"
        except AttributeError:
            return None

    def __match_class_repr__(self) -> str:
        required_values = copy.deepcopy(self.__annotations__)
        for key, val in required_values.items():
            if hasattr(val, "__match_class_repr__"):
                required_values[key] = val.__match_class_repr__()
        return f"{self.cls.__name__}[{required_values}"

    def create_error_msg(self, args: dict) -> str:
        required_values = copy.deepcopy(self.__annotations__)
        for key, val in required_values.items():
            if hasattr(val, "__match_class_repr__"):
                required_values[key] = val.__match_class_repr__()
        return (
            f"Incorrect parameter:\n\t`{pprint.pformat(args, depth=2)}`"
            f"\nRequired parameter:\n`{pprint.pformat(required_values, depth=4)}`"
        )

    def _no_required_inside(self, val) -> bool:
        if get_origin(val) is Required:
            return False
        try:
            new_val = get_args(val)[0]
        except IndexError:
            return True
        else:
            return self._no_required_inside(new_val)

    def check_annotations(self) -> bool:
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

    def __call__(self, *args, **kwargs) -> Type[T]:
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


def match_class_typing(cls: T, **kwargs: Dict[str, Any]) -> T | Any:
    excep_raise = kwargs.pop("excep_raise", TypeMisMatch)
    cache_size = kwargs.pop("cache_size", 1)
    severity = kwargs.pop("severity", "env")

    def __has_annotations__(obj) -> bool:
        return hasattr(obj, "__annotations__")

    def __find_methods(_cls) -> list:
        return [
            func
            for func in dir(_cls)
            if callable(getattr(_cls, func))
            and __has_annotations__(getattr(_cls, func))
            and not hasattr(getattr(_cls, func), "__fe_strng_mtch__")
            and not isinstance(getattr(_cls, func), classmethod)
            and len(list(inspect.signature(getattr(_cls, func)).parameters.keys()))
            > 1  # if it is a function without parameter there is no need to wrap it
        ]

    def __add_decorator(_cls) -> None:
        severity_level: int = _severity_level(severity)
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
                            excep_raise=excep_raise,
                            subclass=is_static,
                            severity=_get_severity_level(severity_level),
                            cache_size=cache_size,
                        ),
                    )
                except TypeError:
                    pass

    def wrapper(some_cls) -> Callable[P, T]:
        def inner(*args, **cls_kwargs):
            __add_decorator(some_cls)
            return some_cls(*args, **cls_kwargs)

        inner._matches_class = True  # type: ignore
        return inner

    if cls is not None:
        from typing import _TypedDictMeta  # type: ignore

        try:
            from typing_extensions import _TypedDictMeta as _TypedDictMetaExtension  # type: ignore
        except ImportError:
            if isinstance(cls, _TypedDictMeta):
                return MatchTypedDict(cls)
        else:
            if isinstance(cls, _TypedDictMeta) or isinstance(cls, _TypedDictMetaExtension):
                return MatchTypedDict(cls)

        __add_decorator(cls)
        cls._matches_class = True  # type: ignore
        return cls
    else:
        return wrapper


def getter(func) -> Any:
    return action(func, "getter", match_typing)


def setter(func) -> Any:
    return action(func, "setter", match_typing)


def getter_setter(func) -> Any:
    return action(func, "getter_setter", match_typing)


class FinalClass:
    def __new__(cls, instance=None, *args, **kwargs) -> "FinalClass":
        if args:
            raise RuntimeError(
                f"`class {instance}` can not inherit from `class {args[0][0].__name__}`"
            )
        cls.cls = instance
        return super().__new__(cls)

    def __init__(self, cls=None, *args, **kwargs):
        self.cls = cls

    def __getattr__(self, item: Any) -> Any:
        return getattr(self.cls, item)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.cls(*args, **kwargs)

    def __repr__(self) -> str:
        return repr(self.cls)

    def __str__(self) -> str:
        return str(self.cls)

    @property
    def __doc__(self) -> str:  # type: ignore
        return self.cls.__doc__
