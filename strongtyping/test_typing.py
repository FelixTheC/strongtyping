#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 30.04.20
@author: felix
"""
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Type
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
    def func_d(a: list, b: List[Union[int, str]]):
        return f"{len(a)}, {len(b)}"

    assert func_d([1, 2], [1, 2, '3', '4']) == '2, 4'


def test_lists_with_unions():

    @match_typing
    def func_e(a: List[Union[str, int]], b: List[Union[str, int, tuple]]):
        return f'{len(a)}-{len(b)}'

    assert func_e([1, '2', 3, '4'], [5, ('a', 'b'), '10'])

    with pytest.raises(TypeMisMatch):
        func_e([5, ('a', 'b'), '10'], [1, '2', 3, datetime.date])


def test_with_any():
    @match_typing
    def func_a(a: Any, b: any):
        return f'{a}-{b}'

    assert func_a(2, '2') == '2-2'
    assert func_a([], ()) == '[]-()'
    assert func_a(datetime, set())


def test_with_optional():

    @match_typing
    def func_a(a: Optional[str], b: Optional[int]):
        return f'{a}-{b}'

    assert func_a(None, None) == 'None-None'
    assert func_a('2', 1) == '2-1'

    with pytest.raises(TypeMisMatch):
        func_a(1, '2')


def test_with_dict():

    @match_typing
    def func_a(a: Dict[str, int], b: Dict[Tuple[str, str], int]):
        return f'{a}-{b}'

    assert func_a({'a': 5, 'b': 2},
                  {('hello', 'world'): 10,
                   ('foo', 'bar'): 6}) == "{'a': 5, 'b': 2}-{('hello', 'world'): 10, ('foo', 'bar'): 6}"

    with pytest.raises(TypeMisMatch):
        func_a({'a': 5, 'b': 2}, {'helloworld': 10, 'foobar': 6})

    with pytest.raises(TypeMisMatch):
        func_a({'a': 5, 'b': 2}, {('hello', 'world'): '2', ('foo', 'bar'): '9'})

    with pytest.raises(TypeMisMatch):
        func_a({'a': 5, 'b': '2'}, {('hello', 'world'): 12, ('foo', 'bar'): 19})

    with pytest.raises(TypeMisMatch):
        func_a({'a': 5, 'b': 2}, {('hello', 'world'): 12, ('foo', 'bar'): '19'})


def test_with_dict_2():
    @match_typing
    def func_b(a: Dict[str, int], b: Dict[Tuple[Tuple[Tuple[str, str], str], str], int]):
        return True

    @match_typing
    def func_c(a: Dict[Union[str, int], int]):
        return True

    assert func_b({'a': 1}, {((('fbar', 'fbar'), 'foo'), 'bar'): 2020})
    assert func_c({'b': 2, 34: 313})

    with pytest.raises(TypeMisMatch):
        assert func_b({'a': 1}, {((('fbar', 1), 'foo'), 'bar'): 2020})

    with pytest.raises(TypeMisMatch):
        assert func_c({'b': 2, 34: 'foo'})


def test_with_set():
    @match_typing
    def func_a(a: Set[Union[str, int]], b: Set[int]):
        return True

    assert func_a({'A', 2, 'b', 4, 'c'}, {1, 2, 3, 4})

    with pytest.raises(TypeMisMatch):
        func_a({'A', 2, 'b', 4, 'c'}, {'A', 2, 'b', 4, 'c'})


def test_with_type():

    class NoUser:
        def __repr__(self):
            return 'NoUser'

    class User:
        def __repr__(self):
            return 'User'

    class BasicUser(User):
        pass

    class ProUser(User):
        pass

    class TeamUser(BasicUser, ProUser):
        pass

    @match_typing
    def func_a(a: Type[User]):
        _a = a()
        return repr(_a)

    @match_typing
    def func_b(a: Type[User], b: Type[Union[BasicUser, ProUser]]):
        _a, _b = a(), b()
        return repr(_a), repr(_b)

    assert func_a(User) == 'User'
    assert func_b(User, TeamUser) == ('User', 'User')

    with pytest.raises(TypeMisMatch):
        func_a(NoUser)

    with pytest.raises(TypeMisMatch):
        func_a(NoUser, User)


def test_with_iterator():

    class Fibonacci:
        def __init__(self, limit):
            self.limit = limit
            self.count = 0
            self.values = []

        def __iter__(self):
            return self

        def __next__(self):
            self.count += 1
            if self.count > self.limit:
                raise StopIteration

            if len(self.values) < 2:
                self.values.append(1)
            else:
                self.values = [self.values[-1], self.values[-1] + self.values[-2]]
            return self.values[-1]

    class NonFibonacci:
        def __init__(self, limit):
            self.limit = limit
            self.count = 0
            self.values = []

    @match_typing
    def func_a(a: Iterator):
        return [f for f in a]

    assert func_a(Fibonacci(5)) == [1, 1, 2, 3, 5]

    with pytest.raises(TypeMisMatch):
        func_a(NonFibonacci(5))


def test_with_callable():

    def dummy_func(a: int, b: str, c: Union[str, int]) -> str:
        return 'success'

    def fail_func(a: int, b: str, c: Union[str, int]) -> int:
        return 42

    @match_typing
    def func_a(a: Callable[[int, str, Union[str, int]], str]):
        return True

    assert func_a(dummy_func)
    with pytest.raises(TypeMisMatch):
        func_a(fail_func)


if __name__ == '__main__':
    pytest.main(['-vv', '-s'])
