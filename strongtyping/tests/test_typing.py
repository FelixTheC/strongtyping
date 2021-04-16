#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 30.04.20
@author: felix
"""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from enum import IntEnum
from types import FunctionType
from types import MethodType
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generator
from typing import Iterator
from typing import List
from unittest import mock

from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing import match_class_typing
from strongtyping.strong_typing_utils import checking_typing_list
from strongtyping.strong_typing_utils import checking_typing_json
from strongtyping.strong_typing_utils import checking_typing_tuple
from strongtyping.strong_typing_utils import checking_typing_type
from strongtyping.strong_typing_utils import checking_typing_set
from strongtyping.strong_typing_utils import checking_typing_dict
from strongtyping.strong_typing_utils import get_possible_types
from strongtyping.strong_typing_utils import get_origins
from strongtyping.strong_typing_utils import TypeMisMatch


try:
    from typing import Literal
except ImportError:
    print('python version < 3.8')
from typing import NewType
from typing import Optional
from typing import Set
from typing import Type
from typing import Union, Tuple

import pytest
import ujson as ujson


def test_get_possible_types_from_typing():
    # using pytest.mark.parametrize is also an option but for the moment this is fine also
    assert get_possible_types(List[str]) == (str, )
    assert get_possible_types(Tuple[str, str]) == (str, str)
    assert get_possible_types(Dict[str, int]) == (str, int)
    assert get_possible_types(List[Union[str, int]]) == (Union[str, int], )
    assert get_possible_types(Union[str, int]) == (str, int, )
    assert get_possible_types(Set[int]) == (int, )
    assert get_possible_types(Tuple[Union[str, int], List[int]]) == (Union[str, int], List[int], )


@pytest.mark.skipif(sys.version_info.minor > 6, reason='some special cases py3.6')
def test_get_origins():
    assert get_origins(List[str]) == (list, 'List')
    assert get_origins(Tuple[str, str]) == (tuple, 'Tuple')
    assert get_origins(Union[str, int]) == (Union, 'Union')
    assert get_origins(FunctionType) == (None, 'None')


def test_check_typing_dict_builtin():
    arg = {'spell': 'lumos'}

    assert checking_typing_dict(arg, ())
    assert checking_typing_dict({1, 2, 3}, ()) is False


def test_check_typing_dict_typ():
    arg = {'spell': 'lumos'}

    assert checking_typing_dict(arg, (str, str))
    assert checking_typing_dict(arg, (str, int)) is False
    assert checking_typing_dict(arg, (int, str)) is False
    assert checking_typing_dict(arg, (Union[int, str], str))
    assert checking_typing_dict(arg, (str, Union[int, str]))


def test_check_typing_set_builtin():
    arg = {'avadra', 'kevadra'}

    assert checking_typing_set(arg, ())
    assert checking_typing_set({'spell': 'lumos'}, ()) is False


def test_check_typing_list_builtin():
    arg = ['avadra', 'kevadra']

    assert checking_typing_list(arg, (str,))
    assert checking_typing_list({'spell': 'lumos'}, ()) is False


def test_check_typing_tuple_builtin():
    arg = ('avadra', 'kevadra')

    assert checking_typing_tuple(arg, None)
    assert checking_typing_tuple(arg, (str, str))
    assert checking_typing_tuple({'spell': 'lumos'}, ()) is False


def test_check_typing_json():
    arg = {'spell': 'lumos'}
    arg_2 = [{'spell': 'lumos'}, {'spell': 'accio'}]
    arg_3 = '[{"spell": "lumos"}, {"spell": "accio"}]'

    assert checking_typing_json(arg, json)
    assert checking_typing_json(arg_2, ujson)
    assert checking_typing_json(arg_3, json)
    assert checking_typing_json({'spell', 'lumos'}, ujson) is False


def test_check_typing_type():
    class User:
        def __repr__(self):
            return 'User'

    assert checking_typing_type(User, (User, ))
    assert checking_typing_type({'spell': 'lumos'}, ()) is False


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

    assert func_e([1, '2', 3, '4'], [5, ('a', 'b'), '10']) == '4-3'

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

    assert func_a({'A', 'b', 'c'}, {1, 2, 3, 4})
    assert func_a({2, 4, 6}, {1, 2, 3, 4})
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


def test_with_functiontype():
    class A:
        def inner_func(self):
            return 'inner_success'

    def dummy_func():
        return 'success'

    @match_typing
    def func_a(a: FunctionType):
        return a()

    assert func_a(dummy_func) == 'success'

    with pytest.raises(TypeMisMatch):
        func_a(A().inner_func)


def test_with_methodtype():
    class A:
        def inner_func(self):
            return 'inner_success'

    def dummy_func():
        return 'success'

    @match_typing
    def func_a(a: MethodType):
        return a()

    assert func_a(A().inner_func) == 'inner_success'

    with pytest.raises(TypeMisMatch):
        func_a(dummy_func)


def test_with_method_and_functiontype():

    class A:
        def inner_func(self):
            return 'inner_success'

    def dummy_func():
        return 'success'

    @match_typing
    def func_a(a: Union[FunctionType, MethodType]):
        return a()

    assert func_a(A().inner_func) == 'inner_success'
    assert func_a(dummy_func) == 'success'

    with pytest.raises(TypeMisMatch):
        func_a(A())


def test_mix():
    @match_typing
    def func_a(a: Dict):
        return True

    assert func_a({'a': 1, 'b': 2})

    with pytest.raises(TypeMisMatch):
        func_a({1, 2, 3})

    @match_typing
    def func_a(a: Tuple):
        return True

    assert func_a((1, 2, 3))
    with pytest.raises(TypeMisMatch):
        func_a([1, 2, 3])

    @match_typing
    def func_a(a: Set):
        return True

    assert func_a({1, 2, 3})
    with pytest.raises(TypeMisMatch):
        func_a({'a': 1, 'b': 2})


def test_with_enum():

    class Shake(Enum):
        VANILLA = 7
        CHOCOLATE = 4
        COOKIES = 9
        MINT = 3

    House = IntEnum('House', 'GRIFFINDOR, SLITHERIN, HUFFELPUFF, RAVENCLAW')

    @match_typing
    def func_a(a: Enum, b: Shake):
        return f'{a.value}-{b.value}'

    assert func_a(Shake.CHOCOLATE, Shake.COOKIES)

    with pytest.raises(TypeMisMatch):
        func_a(Shake.MINT, House.SLITHERIN)


def test_with_kwargs():
    @match_typing
    def func_a(a: Set[Union[str, int]], b: Set[int]):
        return True

    assert func_a(a={1, '2', 3}, b=set([i for i in range(10)]))


def test_with_json():

    @match_typing
    def func_a(a: json, b: ujson):
        return True

    assert func_a(json.dumps({'some': 'json'}), ujson.dumps([{1: 'foo'}, {2: 'bar'}]))
    assert func_a({'some': 'json'}, [{1: 'foo'}, {2: 'bar'}])
    assert func_a(json.dumps({'some': 'json'}, indent=4), ujson.dumps([{1: 'foo'}, {2: 'bar'}, {3: b'foobar'}],
                                                                      reject_bytes=False))

    with pytest.raises(TypeMisMatch):
        func_a({('not', 'allowed'): [i for i in range(5)]}, [{2: b'hello'}, {42: b'world'}])


@pytest.mark.skip()
def test_with_new_type():

    FruitType = NewType('FruitType', Tuple[str, str])

    @match_typing
    def func_a(a: str, b: FruitType):
        return True

    assert func_a('some', FruitType(('apple', 'sweet')))
    assert func_a('free', FruitType(('pineapple', 'super sweet')))

    with pytest.raises(TypeMisMatch):
        # problem with NewType: I only get the supertype and nothing about the name or similar
        # this will be true because the supertype of FruitType is Tuple[str, str]
        # func_a('new', ('coconut', 'soft'))
        func_a('new', ['coconut', 'soft'])

    MyType = NewType('MyType', List[Tuple[str, Dict[str, Union[int, str]]]])

    @match_typing
    def func_a(a: str, b: MyType):
        return True

    assert func_a('some', MyType([('apple', {'foo': 'bar'})]))

    with pytest.raises(TypeMisMatch):
        func_a('new', {'not': 'my_type'})


def test_with_generator():

    @match_typing
    def func_a(a: Generator):
        return True

    assert func_a((i for i in range(10)))
    with pytest.raises(TypeMisMatch):
        func_a([i for i in range(10)])


def test_exception_none():

    @match_typing(excep_raise=None)
    def multipler(a: int, b: int):
        return a * b

    with pytest.warns(RuntimeWarning) as record:
        assert multipler('hello', 3) == 'hellohellohello'
        assert str(record[0].message) == "Incorrect parameters: a: int"


@pytest.mark.skipif(sys.version_info.minor < 8, reason='Literal first available in py3.8')
def test_with_literals():
    @match_typing
    def with_literals(direction: Literal['horizontal', 'vertical']):
        return direction

    assert with_literals('vertical') == 'vertical'
    with pytest.raises(TypeMisMatch):
        with_literals('up')

    @match_typing
    def dict_with_literals(direction: Dict[Literal['horizontal', 'vertical'], float]):
        return direction

    assert dict_with_literals({'vertical': .23}) == {'vertical': .23}


def test_with_class_decorator():

    @match_class_typing
    class Dummy:
        attr = 100

        def a(self, val: int):
            return val * .25

        def b(self):
            return 'b'

        def c(self):
            return 'c'

        def _my_secure_func(self, val: Union[int, float], other: 'Dummy'):
            return val * other.attr

    d = Dummy()

    assert d.a(8) == 2
    assert d.b() == 'b'
    assert d.c() == 'c'

    assert d._my_secure_func(.5, d) == 50

    with pytest.raises(Exception):
        d._my_secure_func(d, .5)


def test_with_class_decorator_init():

    @match_class_typing
    class Dummy:
        attr = 100

        def __init__(self, a):
            self.attr = a

        def a(self, val: int):
            return val * .25

        def b(self):
            return 'b'

    d = Dummy(1)

    assert d.a(8) == 2
    assert d.b() == 'b'


def test_with_class_decorator_no_execption():

    @match_class_typing(excep_raise=None)
    class Dummy:
        attr = 100

        def a(self, val: int):
            return val * 3

        def b(self):
            return 'b'

        def c(self):
            return 'c'

        def _my_secure_func(self, val: Union[int, float], other: 'Dummy'):
            return val * other.attr

    d = Dummy()
    assert d._my_secure_func(.5, d) == 50
    with pytest.warns(RuntimeWarning) as record:
        d.a('Hello RuntimeWarning')
        assert str(record[0].message) == "Incorrect parameters: val: int"


def test_with_class_decorator_and_function_override():

    @match_class_typing
    class Dummy:
        attr = 100

        @match_typing(excep_raise=None)
        def a(self, val: int):
            return val * 3

        def b(self):
            return 'b'

        def c(self):
            return 'c'

        def _my_secure_func(self, val: Union[int, float], other: 'Dummy'):
            return val * other.attr

    d = Dummy()
    assert d._my_secure_func(.5, d) == 50

    with pytest.warns(RuntimeWarning) as record:
        d.a('Hello RuntimeWarning')
        assert str(record[0].message) == "Incorrect parameters: val: int"

    with pytest.raises(Exception):
        d._my_secure_func(d, .5)


def test_with_dataclass():

    @dataclass
    class Dummy:
        attr_a: int
        attr_b: str

    assert Dummy.__annotations__ == {'attr_a': 'int', 'attr_b': 'str'}

    d = Dummy('10', 10)

    assert d.attr_a == '10'
    assert d.attr_b == 10

    @match_class_typing
    @dataclass
    class Dummy:
        attr_a: int
        attr_b: str

    with pytest.raises(TypeMisMatch):
        Dummy('10', 10)


def test_with_severity_param():

    @match_typing
    def a(value: int):
        return value * 2

    assert a(2) == 4
    with pytest.raises(TypeMisMatch):
        a('2')

    @match_typing(severity=SEVERITY_LEVEL.WARNING)
    def a(value: int):
        return value * 2

    assert a(2) == 4
    with pytest.warns(RuntimeWarning) as record:
        a('2')
        assert str(record[0].message) == "Incorrect parameters: value: int"

    @match_typing(severity=SEVERITY_LEVEL.DISABLED)
    def a(value: int):
        return value * 2

    assert a(2) == 4
    assert a('2') == '22'

    @match_class_typing(severity=SEVERITY_LEVEL.WARNING)
    class Dummy:
        attr = 100

        def a(self, val: int):
            return val * 3

        def b(self):
            return 'b'

    d = Dummy()
    assert d.a(2) == 6

    with pytest.warns(RuntimeWarning) as record:
        d.a('2')
        assert str(record[0].message) == "Incorrect parameters: val: int"

    @match_class_typing(severity=SEVERITY_LEVEL.DISABLED)
    class Other:
        attr = 100

        def a(self, val: int):
            return val * 3

        def b(self):
            return 'b'

    dd = Other()
    assert dd.a(2) == 6
    assert dd.a('2') == '222'

    @match_class_typing(severity=SEVERITY_LEVEL.DISABLED)
    class OtherDummy:
        attr = 100

        def __init__(self, val: int):
            self.attr = val * 2

        @match_typing
        def a(self, val: int):
            return val * self.attr

    od = OtherDummy('2')
    assert od.a(2) == '2222'
    with pytest.raises(TypeMisMatch):
        assert od.a('2') == '222'


def test_with_env_severity(monkeypatch):

    monkeypatch.setenv('ST_SEVERITY', 'disable')

    @match_class_typing
    class Dummy:
        attr = 100

        def a(self, val: int):
            return val * 3

    d = Dummy()
    assert d.a('2') == '222'

    @match_typing
    def some_func(val_1: int, val_2: List[int]):
        return [v * val_1 for v in val_2]

    assert some_func(3, ['a', 'b', 'c']) == ['aaa', 'bbb', 'ccc']

    monkeypatch.setenv('ST_SEVERITY', 'warning')

    @match_class_typing
    class Dummy:
        attr = 100

        def a(self, val: int):
            return val * 3

    d = Dummy()
    with pytest.warns(RuntimeWarning):
        assert d.a('2') == '222'

    @match_typing
    def some_func(val_1: int, val_2: List[int]):
        return [v * val_1 for v in val_2]

    with pytest.warns(RuntimeWarning):
        assert some_func(3, ['a', 'b', 'c']) == ['aaa', 'bbb', 'ccc']


def test_classmethod_staticmethod(monkeypatch):
    monkeypatch.setenv('ST_SEVERITY', 'warning')

    @match_class_typing
    class Dummy:
        attr = 100

        @classmethod
        def b(cls):
            return True

        @staticmethod
        def c(val: int):
            return val * 10

        @staticmethod
        @match_typing
        def d(val: int):
            return val * 10

    assert Dummy.b()  # classmethods must be decorated separately
    assert Dummy.c(2) == 20
    assert Dummy.c('2') != 20  # staticmethod can't be checked when called that way

    with pytest.warns(RuntimeWarning):
        assert Dummy.d('2')  # staticmethod must be decorated separately too, to be able to call it that way

    d = Dummy()

    with pytest.warns(RuntimeWarning):
        d.c('2')


@pytest.mark.skipif(sys.version_info.minor < 9, reason='Literal first available in py3.8')
def test_generic_type_hints():

    @match_typing
    def a_dict(val: dict[str, str]):
        return True

    @match_typing
    def b_list(val: list[int]):
        return len(val)

    @match_typing
    def c_tuple(val: tuple[str, str, int]):
        return True

    @match_typing
    def d_set(val: set[str]):
        return len(val)

    assert a_dict({'foo': 'bar'})

    with pytest.raises(TypeMisMatch):
        a_dict({1: 'bar'})

    with pytest.raises(TypeMisMatch):
        a_dict({'foo': [1, 2, 3]})


def test_optional_same_as_union_none():
    AType = List[Tuple[int, str]]
    BType = Dict[str, Union[str, int]]
    CType = Dict[str, int]
    KType = Dict[str, Union[AType, BType, CType, None]]

    @match_typing
    def func_a(x: Union[KType, None] = None):
        if x is not None:
            return 2
        return 1

    assert func_a({'a': {'foo': 2}}) == 2
    assert func_a({'a': [(1, '2'), (3, '4')]}) == 2
    assert func_a({'a': {'foo': 2}}) == 2
    assert func_a(None) == 1

    with pytest.raises(TypeMisMatch):
        func_a(set([1, 2, 3]))

    with pytest.raises(TypeMisMatch):
        func_a({'a': ((1, '2'), (3, '4'))})


@pytest.mark.skipif(bool(int(os.environ['ST_MODULES_INSTALLED'])) is False, reason='not installed module')
def test_strongtyping_modules_integration():
    try:
        from strongtyping_modules.strongtyping_modules import list_elements
        with mock.patch('strongtyping.strong_typing_utils.list_elements',
                        side_effect=list_elements) as mocked_list_module:
            @match_typing
            def some_func(val_1: List[Union[Literal['alpha', 'beta'], int]]):
                return len(val_1)

            try:
                some_func(['alpha', 23, 'beta', 2])
            except TypeMisMatch:
                pass
            assert mocked_list_module.called

    except ImportError:
        pass


if __name__ == '__main__':
    pytest.main(['-vv', '-s', __file__])
