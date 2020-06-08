#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 30.04.20
@author: felix
"""
from typing import List
from typing import Union, Tuple

import pytest

from strongtyping.strong_typing import match_typing, TypeMisMatch


def test_func_without_typing():
    @match_typing
    def func_a(a, b):
        return True

    assert func_a(1, '2') is True


def test_func_keeps_docstring():
    @match_typing
    def func_a(a, b):
        """
        Test abracadabra
        """
        return True

    assert 'Test abracadabra' == func_a.__doc__.strip()
    assert 'func_a' == func_a.__name__


def test_func_with_one_typing_param():
    @match_typing
    def func_a(a, b: int):
        return True

    assert func_a(1, 2) is True


def test_func_with_multiple_typing_param():
    @match_typing
    def func_a(a: str, b: int, c: list):
        return True

    assert func_a('1', 2, [i for i in range(5)])


def test_func_with_union_typing_param():
    @match_typing
    def func_a(a: Union[str, int], b: int, c: Union[list, tuple]):
        return True

    assert func_a(3, 4, ('capacious', 'extremis'))


def test_func_with_tuple_typing():
    @match_typing
    def func_a(a: Tuple[str, str, str]):
        return True

    assert func_a(('Harmonia', 'Nectere', 'Passus'))


def test_func_raise_error_incorrect_parameters_less():
    @match_typing
    def func_a(a: Tuple[str, str, str]):
        return True

    with pytest.raises(TypeMisMatch):
        func_a(a=('Oculus', 'Reparo'))


def test_func_raise_error_incorrect_parameters_much():
    @match_typing
    def func_a(a: Tuple[str, str, str]):
        return True

    with pytest.raises(TypeMisMatch):
        func_a(('Peskipiksi', 'Pesternomi', 'Petrificus', 'Totalus'))


def test_func_with_own_union_type():
    class A:
        pass

    class B:
        pass

    MyType = Tuple[Union[str, int], Union[list, tuple], Union[A, B]]

    @match_typing
    def func_a(a: MyType):
        return True

    assert func_a(a=('Lumos', [1, 2, 3], A()))


def test_func_with_own_union_type():
    class A:
        pass

    class B:
        pass

    MyType = Tuple[Union[str, int], Union[list, tuple], Union[A, B]]

    @match_typing
    def func_a(a: MyType):
        return True

    assert func_a(a=('Lumos', [1, 2, 3], A()))


def test_decorated_class_method():

    class A:
        @match_typing
        def func_a(self, a: int):
            return True

        @staticmethod
        @match_typing
        def func_b(b: str):
            return True

        @classmethod
        @match_typing
        def func_c(cls, c: str):
            return True

    a = A()
    assert a.func_a(2) is True
    assert a.func_b('test success')
    assert A.func_c('test success')


def test_use_different_exception():

    @match_typing(excep_raise=TypeError)
    def func_a(a: str):
        return True

    @match_typing(excep_raise=ValueError)
    def func_b(a: str):
        return True

    with pytest.raises(TypeError):
        func_a(12)

    with pytest.raises(ValueError):
        func_b(22)


def test_use_own_exception():

    class MyException(Exception):
        pass

    @match_typing(excep_raise=MyException)
    def func_a(a: str):
        return True

    with pytest.raises(MyException):
        func_a(12)


def test_use_str_repr_as_type():

    class A:
        @match_typing
        def func_a(self, a: 'A'):
            return True

    class Foo:
        pass

    with pytest.raises(TypeMisMatch):
        b = A()
        b.func_a(Foo())

    b = A()
    assert b.func_a(A())


def test_second_pos_arg_hinted():

    @match_typing
    def func_b(a, b: int):
        return f"{a}, {b}"

    assert func_b(1, 2) == "1, 2"

    assert func_b("1", 2) == "1, 2"  # shouldn't raise a TypeMisMatch

    with pytest.raises(TypeMisMatch):
        assert func_b(1, "2") == "1, 2"  # Should raise a TypeMisMatch

    with pytest.raises(TypeMisMatch):
        assert func_b("1", "2") == "1, 2"


def test_with_lists():

    @match_typing
    def func_b(a, b: List):
        return f"{len(a)}, {len(b)}"

    # assert func_b([1, 2], ['a', 'b', 'c']) == '2, 3'

    with pytest.raises(TypeMisMatch):
        func_b([1, 2], ('a', 'b', 'c')) == '2, 3'

    @match_typing
    def func_c(a: list, b: List[str]):
        return f"{len(a)}, {len(b)}"

    assert func_c([1, 2], ['a', 'b', 'c']) == '2, 3'

    with pytest.raises(TypeMisMatch):
        func_c([1, 2], ('a', 'b', 'c')) == '2, 3'

    with pytest.raises(TypeMisMatch):
        func_c((1, 2), ['a', 'b', 'c']) == '2, 3'

    with pytest.raises(TypeMisMatch):
        func_c([1, 2], [1, 2, 3]) == '2, 3'

    @match_typing
    def func_c(a: list, b: List[int]):
        return f"{len(a)}, {len(b)}"

    assert func_c([1, 2], [1, 2, 3]) == '2, 3'

    @match_typing
    def func_d(a: list, b: Union[List[int], List[str]]):
        return f"{len(a)}, {len(b)}"

    assert func_d([1, 2], [1, 2, '3', '4']) == '2, 4'


if __name__ == '__main__':
    pytest.main(['-vv', '-s'])
