import time
from typing import Union

import pytest
import sttyping

from strongtyping import _c_impl, _py_impl


@pytest.mark.benchmark(group="dict-validation", warmup=False)
def test_performance_python(benchmark):
    data = {str(i): i for i in range(10_000)}
    data["9999"] = "error"
    schema = dict[str, int]
    # Benchmark the Python version
    benchmark(_py_impl.checking_typing_dict, data, schema)


@pytest.mark.benchmark(group="dict-validation", warmup=True)
def test_performance_cython(benchmark):
    data = {str(i): i for i in range(10_000)}
    data["9999"] = "error"
    schema = dict[str, int]
    # Benchmark the Cython version
    benchmark(_c_impl.dict_elements, data, schema, None, None)


@pytest.mark.benchmark(group="dict-validation", warmup=True)
def test_performance_pure_c(benchmark):
    data = {str(i): i for i in range(10_000)}
    data["9999"] = "error"
    schema = dict[str, int]
    # Benchmark the Cython version
    benchmark(sttyping.st_dict, data, schema)


def test_performance_python_():
    data = {str(i): i for i in range(10_000)}
    schema = dict[str, int]
    data["9999"] = "error"
    start = time.perf_counter_ns()
    _py_impl.checking_typing_dict(data, schema)
    print(f"Python duration in ns: {time.perf_counter_ns() - start}")


def test_performance_cython_():
    data = {str(i): i for i in range(10_000)}
    schema = dict[str, int]
    data["9999"] = "error"
    start = time.perf_counter_ns()
    _c_impl.dict_elements(data, schema, None, None)
    print(f"Cython duration in ns: {time.perf_counter_ns() - start}")
