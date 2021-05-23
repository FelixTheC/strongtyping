# Welcome to strongtyping
[![PyPI version](https://badge.fury.io/py/strongtyping.svg)](https://badge.fury.io/py/strongtyping)
![Python application](https://github.com/FelixTheC/strongtyping/workflows/Python%20application/badge.svg)
![Python tox](https://github.com/FelixTheC/strongtyping/workflows/Python%20tox/badge.svg)
![image](https://codecov.io/gh/FelixTheC/strongtyping/graph/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/strongtyping/badge/?version=latest)](https://strongtyping.readthedocs.io/en/latest/?badge=latest)
[![](https://img.shields.io/pypi/dm/strongtyping.svg)](https://pypi.org/project/strongtyping/)
<p>Decorator which <b>checks at Runtime</b> whether the function is called with the correct type of parameters.<br> 
And <b><em>raises</em> TypeMisMatch</b> if the used parameters in a function call where invalid.</p>

### The problem
> > I love python and his freedom but with the new option of adding type hints I wanted to get rid of writing `if isinstance(value, whatever)` in my programs. 
> 
>> In a bigger project, it happened that some developers used a tiny IDE and others a more advanced one which highlighted 
 typing issues. And there the trouble began, we had a bug and after a long debugging session we found out that the issue 
 was a wrong type of an argument, it doesn't crash the program but the output was not what anyone of us had expected.  
> 
> And that only encouraged me even more to tackle this problem.

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

### The solution
I created a decorator called <b>@match_typing</b> which will check at runtime if the parameters which will be used when <br>
calling this function is from the same type as you have defined.<br>

Here are some examples from my tests
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

- A __package__ written by my own in __Cython__ to speed up the time for checking the parameters <br>
  with this package you can achieve a __boost__ by the __factor 3__ and higher
- you only need to install this package via `pip install strongtyping-modules`
- for a detailed information please checkout the readme from [strongtyping_modules](https://github.com/FelixTheC/strongtyping_modules/blob/master/README.md)

