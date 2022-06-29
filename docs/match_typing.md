## match_typing:

### normal decorator
```python
from strongtyping.strong_typing import match_typing

@match_typing
def foo_bar(a: str, b: int, c: list):
    ...
```

### class method decorator
```python
from strongtyping.strong_typing import match_typing

class Foo:
    ...
    @match_typing
    def foo_bar(self, a: int):
        ...
```

### mix typed and untyped parameters 
- by default, only parameters with type hints are checked at runtime
- you're also able to specify exactly which type hint(s) you want to "secure":
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

### add your own exception
- with `excep_raise`
```python
from strongtyping.strong_typing import match_typing

class SomeException(Exception):
    pass

@match_typing(excep_raise=SomeException)
def foo_bar(with_type_a: str, without_type_a, with_type_b: list, without_type_b):
    ...
```

### enable internal cache
- with `cache_size` = 1
```python
from strongtyping.strong_typing import match_typing

class MyClass:
    pass

@match_typing(cache_size=1)
def foo_bar(a: tuple, b: MyClass):
    ...
```

### disable Exception
  - You can also __disable__ the raising of an __Exception__ and get a __warning__ instead.  This means your function will execute even when the parameters are wrong, but you're advised to only use this if you're sure you know what you're doing!
```python
from strongtyping.strong_typing import match_typing

@match_typing(excep_raise=None)
def multipler(a: int, b: int):
    return a * b

print(multipler('Hello', 4))
"""
/StrongTyping/strongtyping/docs.py:208: RuntimeWarning: Incorrect parameter: [a] `'Hello'`
	required: <class 'int'>
  warnings.warn(msg, RuntimeWarning)
HelloHelloHelloHello
"""
```

### Limitations

The current version of `strongtyping` supports:

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
- with string types representation like _[Ed: Not sure what this means Felix?]_
