import inspect
from time import perf_counter

import pytest

from strongtyping.astrong_typing import a_match_typing
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.exceptions import TypeMismatch
from strongtyping.strong_typing import match_typing


@a_match_typing(cache_size=0)
async def simple_func(a: int, b: int) -> int:
    return a + b


@a_match_typing(cache_size=0)
async def func_2(val: list[str], val2: int) -> str:
    return val[val2]


@pytest.mark.asyncio
async def test_async_function_returns_awaitable() -> None:
    assert inspect.iscoroutinefunction(simple_func)


@pytest.mark.asyncio
async def test_async_function_returns_result() -> None:
    assert await simple_func(1, 2) == 3


@pytest.mark.asyncio
async def test_async_function_rejects_invalid_positional_argument() -> None:
    with pytest.raises(TypeMismatch):
        await simple_func(1, "2")


@pytest.mark.asyncio
async def test_async_function_rejects_invalid_keyword_argument() -> None:
    with pytest.raises(TypeMismatch):
        await simple_func(a=1, b="2")


@pytest.mark.asyncio
async def test_async_function_validates_container_contents() -> None:
    assert await func_2(["a", "b"], 1) == "b"

    with pytest.raises(TypeMismatch):
        await func_2(["a", 2], 1)  # type: ignore[list-item]


@pytest.mark.asyncio
async def test_async_function_validates_multiple_nested_dicts() -> None:
    @a_match_typing(cache_size=0)
    async def function(payload: dict[str, dict[str, dict[str, int]]]) -> int:
        return payload["request"]["metadata"]["attempt"]

    valid_payload = {"request": {"metadata": {"attempt": 3}}}
    assert await function(valid_payload) == 3

    invalid_payloads = (
        {1: {"metadata": {"attempt": 3}}},
        {"request": {1: {"attempt": 3}}},
        {"request": {"metadata": {"attempt": "3"}}},
    )
    for invalid_payload in invalid_payloads:
        with pytest.raises(TypeMismatch):
            await function(invalid_payload)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_async_function_validates_large_container_contents() -> None:
    @a_match_typing(cache_size=0)
    async def function(values: list[str]) -> int:
        return len(values)

    values = ["value"] * 10_000
    assert await function(values) == 10_000

    values[-1] = 1  # type: ignore[list-item]
    with pytest.raises(TypeMismatch):
        await function(values)


@pytest.mark.asyncio
async def test_async_and_sync_runtime_for_large_nested_dict() -> None:
    payload = {str(index): {"value": index} for index in range(10_000)}

    @match_typing(cache_size=0)
    def sync_function(values: dict[str, dict[str, int]]) -> int:
        return len(values)

    @a_match_typing(cache_size=0)
    async def async_function(values: dict[str, dict[str, int]]) -> int:
        return len(values)

    # Start the worker thread before timing the async type checks.
    assert await async_function(payload) == len(payload)

    repetitions = 3
    sync_started = perf_counter()
    for _ in range(repetitions):
        assert sync_function(payload) == len(payload)
    sync_duration = perf_counter() - sync_started

    async_started = perf_counter()
    for _ in range(repetitions):
        assert await async_function(payload) == len(payload)
    async_duration = perf_counter() - async_started

    # Thread scheduling has an inherent cost; this only detects major regressions.
    assert async_duration < sync_duration * 20


@pytest.mark.asyncio
async def test_async_function_can_use_a_custom_exception() -> None:
    class InvalidArgument(Exception):
        pass

    @a_match_typing(excep_raise=InvalidArgument, cache_size=0)
    async def function(value: int) -> int:
        return value

    with pytest.raises(InvalidArgument):
        await function("invalid")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_async_function_can_warn_instead_of_raise() -> None:
    @a_match_typing(excep_raise=None, cache_size=0)
    async def function(value: int) -> str:
        return str(value)

    with pytest.warns(RuntimeWarning):
        assert await function("invalid") == "invalid"  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_async_function_can_disable_validation() -> None:
    @a_match_typing(severity=SEVERITY_LEVEL.DISABLED, cache_size=0)
    async def function(value: int) -> str:
        return str(value)

    assert await function("not validated") == "not validated"  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_async_function_can_use_duck_typing() -> None:
    @a_match_typing(allow_duck_typing=True, cache_size=0)
    async def function(value: float) -> float:
        return value

    assert await function(1) == 1


@pytest.mark.asyncio
async def test_async_function_validates_annotated_return_values() -> None:
    @a_match_typing(validate_return=True, cache_size=0)
    async def function() -> int:
        return "invalid"  # type: ignore[return-value]

    with pytest.raises(TypeMismatch):
        await function()


@pytest.mark.asyncio
async def test_async_function_cache_returns_the_awaited_result() -> None:
    calls = 0

    @a_match_typing(cache_size=1)
    async def function(value: int) -> int:
        nonlocal calls
        calls += 1
        return value

    assert await function(1) == 1
    assert await function(1) == 1
    assert calls == 2


@pytest.mark.asyncio
async def test_async_function_cache_does_not_accept_different_argument_types() -> None:
    @a_match_typing(cache_size=1)
    async def function(value: int) -> int:
        return value

    assert await function(2) == 2

    with pytest.raises(TypeMismatch):
        await function("2")  # type: ignore[arg-type]
