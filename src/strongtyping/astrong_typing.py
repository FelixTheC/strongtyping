import asyncio
import inspect
import pprint
import traceback
import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any

from strongtyping._utils import (
    CACHE_IGNORE_CLASS_FUNCTIONS,
    _error_info_msg,
    get_safe_cache_key,
    get_severity_level,
    remove_subclass,
)
from strongtyping.cached_set import CachedSet
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.exceptions import TypeMismatch
from strongtyping.strong_typing_utils import (
    check_type,
    default_return_queue,
    get_origins,
)


async def _raise_error_or_warning(
    msg: str,
    failed_params: tuple[str, ...],
    annotated_values: Any,
    annotations: Any,
    excep_raise: type[Exception] = TypeMismatch,
    severity_level: int = SEVERITY_LEVEL.ENABLED.value,
) -> None:
    if excep_raise is not None and severity_level == SEVERITY_LEVEL.ENABLED.value:
        raise excep_raise(msg, failed_params, annotated_values, annotations) from None
    else:
        warnings.warn(msg, RuntimeWarning)


def a_match_typing(
    _func: Callable[..., Any] | None = None,
    *,
    excep_raise: type[Exception] = TypeMismatch,
    subclass: bool = False,
    severity: str = "env",
    **kwargs: Any,
) -> Any:
    cached_enabled: int = kwargs.get("cache_size", 1)
    cached_set = CachedSet(cached_enabled) if cached_enabled > 0 else None
    check_duck_typing = kwargs.get("allow_duck_typing", False)
    validate_return = kwargs.get("validate_return", False)

    def wrapper(func: Callable[..., Any]) -> Any:
        arg_names = [name for name in inspect.signature(func).parameters]
        annotations = func.__annotations__
        severity_level = get_severity_level(severity)

        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            if arg_names and severity_level > SEVERITY_LEVEL.DISABLED.value:
                args = remove_subclass(args, subclass)
                arg_vals, kwarg_vals = get_safe_cache_key(args, kwargs)
                cached_key = (func, arg_vals, kwarg_vals)

                if (
                    cached_set is not None
                    and func.__name__ not in CACHE_IGNORE_CLASS_FUNCTIONS
                    and cached_key in cached_set
                ):
                    print(cached_set)
                    # check if func with args and kwargs was checked once before with positive result
                    return await func(*args, **kwargs)

                # Thanks to Ruud van der Ham who find a better and more stable solution for check_args
                failed_params = []
                for arg, arg_name in zip(args, arg_names):
                    if not await asyncio.to_thread(
                        check_type,
                        arg,
                        annotations.get(arg_name),
                        mro=False,
                        check_duck_typing=check_duck_typing,
                    ):
                        failed_params.append(arg_name)

                failed_unpacking = False

                if anno_kwargs := annotations.get("kwargs"):
                    if not await asyncio.to_thread(
                        check_type,
                        kwargs,
                        anno_kwargs,
                        mro=False,
                        check_duck_typing=check_duck_typing,
                    ):
                        failed_unpacking = True
                else:
                    for kwarg_name, kwarg in kwargs.items():
                        if not await asyncio.to_thread(
                            check_type,
                            kwarg,
                            annotations.get(kwarg_name, annotations.get("kwargs")),
                            mro=False,
                            check_duck_typing=check_duck_typing,
                        ):
                            failed_params.append(kwarg_name)

                if not default_return_queue.empty():
                    return default_return_queue.queue.pop()

                if failed_params or failed_unpacking:
                    annotated_values = {arg_name: arg for arg, arg_name in zip(args, arg_names)}

                    for kwarg_name, kwarg in kwargs.items():
                        annotated_values[kwarg_name] = kwarg
                    root = next(iter(traceback.extract_stack(None, 2)))

                    source = f"{root.filename}:{root.lineno} in {root.name}"
                    msg_list = "\n".join(
                        _error_info_msg.substitute(
                            source=source,
                            expected_type=annotations.get(name, name),
                            actual_value=annotated_values[name],
                            actual_type=type(annotated_values[name]),
                        )
                        for name in failed_params
                    )

                    if failed_unpacking:
                        msg_list += f"""The kwargs: {kwargs} can not be packed into a {annotations["kwargs"].__args__[0]} TypedDict.\n
                        Which requires following parameters\n\t{annotations["kwargs"].__args__[0].__annotations__}."""

                    msg = f"\n{msg_list}"

                    await _raise_error_or_warning(
                        msg,
                        failed_params,
                        annotated_values,
                        annotations,
                        excep_raise,
                        severity_level,
                    )

                if cached_set is not None and func.__name__ not in CACHE_IGNORE_CLASS_FUNCTIONS:
                    cached_set.add(cached_key)

            if annotations.get("return"):
                return_type = annotations.get("return")
                if validate_return or get_origins(return_type)[1] == "TypeGuard":
                    return_val = await func(*args, **kwargs)
                    if not await asyncio.to_thread(check_type, return_val, return_type, mro=False):
                        await _raise_error_or_warning(
                            f"Incorrect return value: `{pprint.pformat(return_val, width=20, depth=2)}`",
                            ("return",),
                            return_type,
                            annotations,
                            excep_raise,
                            severity_level,
                        )
                    return return_val
                else:
                    return await func(*args, **kwargs)
            else:
                return await func(*args, **kwargs)

        _inner: Any = inner
        _inner.__fe_strng_mtch__ = 0
        return _inner

    if _func is not None:
        return wrapper(_func)
    else:
        return wrapper
