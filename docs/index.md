# Welcome to `strongtyping`

[![PyPI version](https://badge.fury.io/py/strongtyping.svg)](https://badge.fury.io/py/strongtyping)
![Python application](https://github.com/FelixTheC/strongtyping/workflows/Python%20application/badge.svg)
![Python tox](https://github.com/FelixTheC/strongtyping/workflows/Python%20tox/badge.svg)
![image](https://codecov.io/gh/FelixTheC/strongtyping/graph/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/strongtyping/badge/?version=latest)](https://strongtyping.readthedocs.io/en/latest/?badge=latest)
[![](https://img.shields.io/pypi/dm/strongtyping.svg)](https://pypi.org/project/strongtyping/)


<p><b><em>strongtyping</em></b> gives you a handy decorator which checks <b>at runtime</b> whether a function has been called with the correct parameter types.<br> 
It raises <b><em>TypeMisMatch</em></b> if the parameters used in a function call are invalid.</p>

### The Problem

Even if you use an advanced IDE which can highlight typing issues, in bigger projects you'll probably find yourself struggling through long debugging sessions before realising the issue was due to the _wrong type of argument_.  These bugs are tricky to spot because they don't necessarily crash the program, but the output is still unexpected or just plain wrong.  For example:

```python
>>> def multiplier(a: int, b: int):
...     return a * b


>>> product = multiplier(3, 4)
12

>>> product_2 = multiplier('Hello', 'World') # Will be highlighted in some IDE's
TypeError

>>> product_3 = multiplier('Hello', 4)
'HelloHelloHelloHello'
# No Exception but the result isn’t really what we expect
```
___
Without `strongtyping` you have to check for every valid type of every parameter in every function, which creates a lot of noisy/bloated code and begs the questions "Why use Python type hinting at all?":
___

```python
>>> def multipler(a: int, b: int):
...     if isinstance(a, int) and isinstance(b, int):
...         return a * b

```

### The Solution

![](https://media.giphy.com/media/L0Z4qwdwv62cn4haFp/giphy.gif)

I love Python and its freedom, but with the new option of adding _type hints_ I wanted to get rid of writing `if isinstance(value, whatever)` repeatedly in my programs, so I decided to create `strongtyping`...

My solution is a simple decorator called `@match_typing` which will check <b>at runtime</b> whether the parameters you provide to a function are valid, based on type hints you've already defined in the `def` line.  Here are some examples:
 
```python
from typing import List, Union
import datetime
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

## Requirements
<b>Python 3.7, 3.8, 3.9</b>

- ujson
- pytest
 

## What's included
#### from strongtyping.strong_typing import

* `@match_typing`
* `@match_class_typing`
* `@getter`
* `@setter`
* `@getter_setter`

#### from strongtyping.type_namedtuple import 
* `typed_namedtuple`

#### from strongtyping.docs_from_typing import
* `@rest_docs_from_typing`
* `@numpy_docs_from_typing`


## Extension
#### strongtpying_module

- A __package__ I wrote in __Cython__ to speed up parameter checking.  This package provides a speed boost of __over 300%__.
- you can simply install this package with `pip install strongtyping-modules`
- for more detailed information please check out the [README](https://github.com/FelixTheC/strongtyping_modules/blob/master/README.md)

