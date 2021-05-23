## match_class_typing
- This decorator will cover each class function automatically with the `@match_typing` decorator:
 
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
- You can also disable the raising of Exceptions and/or internal caching:
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
- Single class methods inside of a previously decorated class can be overwritten with the `@match_typing` decorator
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
