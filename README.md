[![PyPI version](https://badge.fury.io/py/strongtyping.svg)](https://badge.fury.io/py/strongtyping)
![Python application](https://github.com/FelixTheC/strongtyping/workflows/Python%20application/badge.svg)
![image](https://codecov.io/gh/FelixTheC/strongtyping/graph/badge.svg)


# Strong Typing
<p>Decorator which <b>checks at Runtime</b> whether the function is called with the correct type of parameters.<br> 
And <b><em>raises</em> TypeMisMatch</b> if the used parameters in a function call where invalid.</p>
 
## Included decorators

| from strongtyping.strong_typing import            | description                           |
| :-------------                                    | ----------:                           |
| [match_typing](#getting-started)                  | decorator for a function              |
| [match_class_typing](#match_class_typing)         | decorator for a class                 |
| [setter](#setter)                                 | property decorator for set            |
| [getter_setter](#getter_setter)                   | property decorator for get and set    |

| from strongtyping.docstring_typing import         | description                           |
| :-------------                                    | ----------:                           |
| [match_docstring](#reST-docstrings)               | decorator for a function              |
| [match_class_docstring](#match_class_docstring)   | decorator for a class                 |


### The problem:
- Highlighting
    - __Some__ IDE's will/can highlight that one of the parameters in a function call doesn't match but you can execute the function.
- Exception??
    - When the call raise an Exception then we know what to do but sometimes we don't get an Exception only a weird result.

```python
def multipler(a: int, b: int):
    return a * b


product = multipler(3, 4)
# >>> 12

product_2 = multipler('Hello', 'World') # Will be highlighted in some IDE's
# >>> TypeError

product_3 = multipler('Hello', 4)
# >>> 'HelloHelloHelloHello'
# No Exception but the result isn’t really what we expect
```
___
Now we can say that we will check the types in the function body to prevent this.
___

```python
def multipler(a: int, b: int):
    if isinstance(a, int) and isinstance(b, int):
        return a * b
    ...
```
But when your function needs a lot of different parameters with different types you have to create a lot of noising code.<br>
And why should we then use typing in our parameters??

### My solution:
I created a decorator called <b>@match_typing</b> which will check at runtime if the parameters which will be used when <br>
calling this function is from the same type as you have defined.<br><br>
Here are some examples from my tests
```python
# more imports
from strongtyping.strong_typing import match_typing

@match_typing
def func_a(a: str, b: int, c: list):
    ...

func_a('1', 2, [i for i in range(5)])
# >>> True

func_a(1, 2, [i for i in range(5)])
# >>> will raise a TypeMismatch Exception

@match_typing
def func_e(a: List[Union[str, int]], b: List[Union[str, int, tuple]]):
    return f'{len(a)}-{len(b)}'

func_e([1, '2', 3, '4'], [5, ('a', 'b'), '10'])
# >>> '4-3'

func_e([5, ('a', 'b'), '10'], [1, '2', 3, datetime.date])
# >>> will raise a TypeMismatch Exception
```
> I love python and his freedom but with the new option of adding type hints I wanted to get rid of writing `if isinstance(value, whatever)` in my programs. 
> 
>> In a bigger project, it happened that some developers used a tiny IDE and others a more advanced one which highlighted 
 typing issues. And there the trouble began, we had a bug and after a long debugging session we found out that the issue 
 was a wrong type of an argument, it doesn't crash the program but the output was not what anyone of us had expected.  
> 
> And that only encouraged me even more to tackle this problem.


## Getting Started

- normal decorator
```python
from strongtyping.strong_typing import match_typing

@match_typing
def foo_bar(a: str, b: int, c: list):
    ...
```

- class method decorator
```python
from strongtyping.strong_typing import match_typing

class Foo:
    ...
    @match_typing
    def foo_bar(self, a: int):
        ...
```

- use a mix of typed and untyped parameters but then only the typed parameters are checked on runtime
```python
from strongtyping.strong_typing import match_typing

@match_typing
def foo_bar(with_type_a: str, without_type_a, with_type_b: list, without_type_b):
    ...

# no exception
foo_bar('hello', 'world', [1, 2, 3], ('a', 'b'))

# will raise an exception
foo_bar(123, 'world', [1, 2, 3], ('a', 'b'))
```

- add your own exception
```python
from strongtyping.strong_typing import match_typing

class SomeException(Exception):
    pass

@match_typing(excep_raise=SomeException)
def foo_bar(with_type_a: str, without_type_a, with_type_b: list, without_type_b):
    ...
```

- enable internal cache with cache_size = 1
```python
from strongtyping.strong_typing import match_typing

class MyClass:
    pass

@match_typing(cache_size=1)
def foo_bar(a: tuple, b: MyClass):
    ...
```

- disable Exception
    - You can also __disable__ the raise of an __Exception__ and get a __warning instead__ this means your function will <br>
    execute even when the parameters are wrong <b>use only when you know what you're doing</b>
```python
from strongtyping.strong_typing import match_typing

@match_typing(excep_raise=None)
def multipler(a: int, b: int):
    return a * b

print(multipler('Hello', 4))
"""
/StrongTyping/strongtyping/strong_typing.py:208: RuntimeWarning: Incorrect parameters: a: <class 'int'>
  warnings.warn(msg, RuntimeWarning)
HelloHelloHelloHello
"""
```

#### At the current state, it will work with

- builtin types like: str, int, tuple etc
- from typing: 
    - List
    - Tuple
    - Union also nested ( Tuple[Union[str, int], Union[list, tuple]] )
    - Any
    - Dict
    - Set
    - Type
    - Iterator
    - Callable
    - Generator
    - Literal
- from types:
    - FunctionType
    - MethodType
- with string types representation like

```python
from strongtyping.strong_typing import match_typing

class A:
    @match_typing
    def func_a(self, a: 'A'):
        ...
```
- [Back to top](#strong-typing)

## match_class_typing
- this decorator will cover each class function automatically with the __match_typing__ decorator
 
```python
from strongtyping.strong_typing import match_class_typing

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
```
- this decorator supports also disabling of raising Exception and internal caching
```python
from strongtyping.strong_typing import match_class_typing

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

```
- single class methods inside of a allready decorated class can be overwritten with the match_typing decorator
```python
from strongtyping.strong_typing import match_class_typing
from strongtyping.strong_typing import match_typing

@match_class_typing
class Dummy:
    attr = 100

    @match_typing(excep_raise=None)  # this decorator will be used
    def a(self, val: int):
        return val * 3

    def b(self):
        return 'b'

    def c(self):
        return 'c'

    def _my_secure_func(self, val: Union[int, float], other: 'Dummy'):
        return val * other.attr
```
- [Back to top](#strong-typing)

## setter
this decorator can replace your *@foo.setter* from property and check your typing
- this is an extension of [easy_property](https://github.com/salabim/easy_property)
```python
from strongtyping.strong_typing import setter

class Dummy:
    attr = 100
    val = 'foo'

    @setter
    def b(self, val: str):
        self.val = val

d = Dummy()
d.b == 'foo'  # will raise AttributeError 

d.b = 'bar'  # works like a charm

d.b = 1  # will raise TypeMisMatch
```
- [Back to top](#strong-typing)

## getter_setter
this decorator can replace *@propery* from property and check your typing
- this is an extension of [easy_property](https://github.com/salabim/easy_property)
```python
from strongtyping.strong_typing import getter_setter

class Dummy:
    attr = 100

    @getter_setter  # here you will have all in one place (DRY) 
    def c(self, val: int = None):
        if val is not None:
            self.attr = val
        return self.attr

d = Dummy()
d.c == 100  # works like a charm

d.c = 1  # works like a charm

d.c = 'foobar'  # will raise TypeMisMatch
```
- [Back to top](#strong-typing)

## reST docstrings
When working with docstrings in reST style format use the decorator __match_docstring__
```python
from strongtyping.docstring_typing import match_docstring

@match_docstring
def func_a(a):
    """
    :param a:
    :type a: list
    ...
    """

@match_docstring
def func_a(a, b):
    """
    :param int a: foo
    :vartype b: str
    ...
    """

@match_docstring
def func_a(a, b):
    """
    :parameter int a: foo
    :argument str b: bar
    ...
    """
```
At the current state, it will work with basically everything which is written here
https://gist.github.com/jesuGMZ/d83b5e9de7ccc16f71c02adf7d2f3f44

- extended with support for 
    - Iterator
    - Callable
    - Generator
    - FunctionType
    - MethodType

please check __tests/test_typing__ to see what is supported and if something is missing feel free to create an issue.
- [Back to top](#strong-typing)

## match_class_docstring
- this decorator will cover each class function automatically with the __match_docstring__ decorator
```python
from strongtyping.docstring_typing import match_class_docstring

@match_class_docstring
class Dummy:
    attr = 100

    def a(self, val: int):
        """
        :param int val: foo
        """
        return val * .25

    def b(self):
        return 'b'

    def c(self):
        return 'c'

    def _my_secure_func(self, val, other):
        """
        :param val: foo
        :type val: int or float
        :param other: Dummy
        :return:
        """
        return val * other.attr
```
- this decorator supports also disabling of raising Exception and internal caching

```python
from strongtyping.docstring_typing import match_class_docstring

@match_class_docstring(excep_raise=None)
class Dummy:
    attr = 100

    def a(self, val: int):
        """
        :param int val: foo
        """
        return val * 5

    def b(self):
        return 'b'

    def c(self):
        return 'c'

    def _my_secure_func(self, val, other):
        """
        :param val: foo
        :type val: int or float
        :param other: this class
        :type other: Dummy
        :return:
        """
        return val * other.attr
```
- single class methods inside of a allready decorated class can be overwritten with the match_docstring decorator
```python
from strongtyping.docstring_typing import match_class_docstring
from strongtyping.docstring_typing import match_docstring

@match_class_docstring
class Other:
    attr = 100

    def a(self, val: int):
        """
        :param int val: foo
        """
        return val * 2

    def b(self):
        return 'b'

    def c(self):
        return 'c'

    @match_docstring(excep_raise=None)  # this decorator will be used
    def _my_secure_func(self, other):
        """
        :param other: instance of same class
        :type other: Other
        :return:
        """
        return 2 * other.attr
```
- [Back to top](#strong-typing)
<br>

## Package

### Tested for Versions
- 3.6, 3.7, 3.8, 3.9.0b4

### Installing
- pip install strongtyping

#### Versioning
- For the versions available, see the tags on this repository.

### Authors
- Felix Eisenmenger

### License
- This project is licensed under the MIT License - see the LICENSE.md file for details

### Special thanks
- Thanks to Ruud van der Ham for helping me to improve my code and for his [easy_property](https://github.com/salabim/easy_property) package
- Thanks to Dan Bader who puts this package into [PyCoder’s Weekly Issue #428 (July 7, 2020)](https://pycoders.com/issues/428)
- And all how gave me Feedback in the Pythonista Cafe