#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 16.06.20
@author: felix
"""
import pytest

from strongtyping.docstring_typing import match_docstring
from strongtyping.strong_typing import TypeMisMatch


def test_with_docstring_list():

    @match_docstring
    def func_a(a):
        """
        :param a:
        :type a: list
        :return:
        """
        return len(a)

    assert func_a(list(range(10))) == 10
    with pytest.raises(TypeMisMatch):
        func_a(tuple(range(10)))

    @match_docstring
    def func_a(a):
        """
        :param a:
        :type a: list(int)
        :return:
        """
        return len(a)

    assert func_a(list(range(10))) == 10
    with pytest.raises(TypeMisMatch):
        func_a([str(i) for i in range(10)])

    @match_docstring
    def func_a(a):
        """
        :param a:
        :type a: list(int or str)
        :return:
        """
        return len(a)

    dummy_list = list(range(10))
    dummy_list.extend([str(i) for i in range(10)])
    assert func_a(dummy_list) == 20
    with pytest.raises(TypeMisMatch):
        func_a([[i] for i in range(10)])


def test_with_docstring_tuple():

    @match_docstring
    def func_a(a, b):
        """
        :param a: foo
        :type a: list
        :param b: bar
        :type b: tuple
        :return:
        """
        return len(a) + len(b)

    assert func_a(list(range(10)), tuple(range(10))) == 20
    with pytest.raises(TypeMisMatch):
        func_a(tuple(range(10)), list(range(10)))

    @match_docstring
    def func_a(a, b):
        """
        :param a: foo
        :type a: tuple(str, str)
        :param b: bar
        :type b: tuple[int, int]
        :return:
        """
        return len(a) + len(b)

    assert func_a(('foo', 'bar'), (1, 2)) == 4
    with pytest.raises(TypeMisMatch):
        func_a((1, 2), ('foo', 'bar'))
    with pytest.raises(TypeMisMatch):
        func_a((1, 2, 3), ('foo', 'bar'))
    with pytest.raises(TypeMisMatch):
        func_a((1, 2), ('foo', 'bar', 'foobar'))


def test_with_docstring_set():

    @match_docstring
    def func_a(a, b, c):
        """
        :param a: foo
        :type a: list
        :param b: bar
        :type b: tuple
        :param c: foobar
        :type c: set
        :return:
        """
        return len(a) + len(b) + len(c)

    assert func_a(list(range(10)), tuple(range(10)), set(range(10))) == 30
    with pytest.raises(TypeMisMatch):
        func_a(tuple(range(10)), set(range(10)), list(range(10)))


def test_with_docstring_dict():
    @match_docstring
    def func_a(a, c):
        """
        :param a: foo
        :type a: dict
        :param c: foobar
        :type c: set
        :return:
        """
        return len(a) + len(c)

    assert func_a({'a': 'foo', 'b': 'bar'},  set(range(10))) == 12
    with pytest.raises(TypeMisMatch):
        func_a(set(range(10)), {'a': 'foo', 'b': 'bar'})

    @match_docstring
    def func_a(a, b):
        """
        :type a: dict(str, int)
        :type b: dict[str, int]
        """
        return len(a) + len(b)

    assert func_a({'foo': 1, 'bar': 2}, b={'jon': 42, 'doe': 72}) == 4
    with pytest.raises(TypeMisMatch):
        func_a({'foo': '1', 'bar': 2}, b={'jon': 42, 'doe': 72})
    with pytest.raises(TypeMisMatch):
        func_a({'foo': 1, 'bar': 2}, b={'jon': 42, 'doe': '72'})


def test_with_docstring_int_str_bool_float():

    @match_docstring
    def func_a(a, b, c, d):
        """
        :param a: foo
        :type a: int
        :param b: foobar
        :type b: str
        :param c: foobar
        :type c: bool
        :param d: barfoo
        :type d: float
        :return:
        """
        return f'{a} + {b} + {d} = {c}'

    assert func_a(a=1, b='3', c=False, d=.5) == '1 + 3 + 0.5 = False'
    with pytest.raises(TypeMisMatch):
        func_a(set(range(10)), {'a': 'foo', 'b': 'bar'}, list(range(3)), '10')


def test_with_docstring_or():

    @match_docstring
    def func_a(a, b):
        """
        :param a: foo
        :type a: int or float
        :param b: foobar
        :type b: str or list
        """
        return True

    assert func_a(1, 'jon doe')
    assert func_a(.25, list('jane doe'))
    with pytest.raises(TypeMisMatch):
        func_a('1', 42)
        func_a([1, 2, 3], {1, 2, 3})


def test_with_docstring_type_in_param():

    @match_docstring
    def func_a(a, b):
        """
        :param int a: foo
        :param str b: foobar
        """
        return b * a

    assert func_a(3, 'hello') == 'hellohellohello'
    with pytest.raises(TypeMisMatch):
        func_a('hello', 3)


def test_with_docstring_function_method_type():

    class D:

        def some_func(self) -> str:
            return 'Hello'

    def dummy() -> str:
        return 'World'

    @match_docstring
    def func_a(a, b):
        """
        :param MethodType a: foo
        :param FunctionType b: bar
        """
        return b(), a()

    assert func_a(D().some_func, dummy) == ('World', 'Hello')
    with pytest.raises(TypeMisMatch):
        func_a(dummy, D().some_func)


def test_with_docstring_callable():

    class D:

        def some_func(self) -> str:
            return 'Hello'

    def dummy() -> str:
        return 'World'

    @match_docstring
    def func_a(a, b):
        """
        :param Callable a: foo
        :param Callable b: bar
        """
        return b(), a()

    assert func_a(D().some_func, dummy) == ('World', 'Hello')
    with pytest.raises(TypeMisMatch):
        func_a(dummy, [1, 2, 3])


def test_with_docstring_iterator():

    @match_docstring
    def func_a(a, b):
        """
        :param Iterator a: foo
        :param Generator b: bar
        """
        return True

    assert func_a(iter(range(10)), (i for i in range(10)))
    with pytest.raises(TypeMisMatch):
        func_a((i for i in range(10)), iter(range(10)))
    with pytest.raises(TypeMisMatch):
        func_a([1, 2, 3], (21, 42, 71))


def test_with_docstring_mix_param_type():

    @match_docstring
    def func_a(a, b):
        """
        :param int a: foo
        :param b: bar
        :type b: str
        """
        return b * a

    assert func_a(3, 'ni') == 'ninini'
    with pytest.raises(TypeMisMatch):
        func_a('ni', 3)


def test_with_docstring_diff_naming():

    @match_docstring
    def func_a(a, b):
        """
        :param int a: foo
        :vartype b: str
        """
        return b * a

    assert func_a(3, 'ni') == 'ninini'
    with pytest.raises(TypeMisMatch):
        func_a('ni', 3)

    @match_docstring
    def func_a(a, b):
        """
        :parameter int a: foo
        :argument str b: bar
        """
        return b * a

    assert func_a(3, 'ni') == 'ninini'
    with pytest.raises(TypeMisMatch):
        func_a('ni', 3)

    @match_docstring
    def func_a(a, b):
        """
        :arg int a: foo
        :keyword str b: bar
        """
        return b * a

    assert func_a(3, 'ni') == 'ninini'
    with pytest.raises(TypeMisMatch):
        func_a('ni', 3)


if __name__ == '__main__':
    pytest.main(['-vv', '-s', __file__])
