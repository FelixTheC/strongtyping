## SEVERITY_LEVEL

- With the argument `severity` you can control the behavior of `match_typing` and `match_class_typing`
  
- There are three different levels:

| from strongtyping.config import SEVERITY_LEVEL | description|
| :-------------                                 | :----------|
| SEVERITY_LEVEL.ENABLED | the default value, runtime type checking is enabled |
| SEVERITY_LEVEL.WARNING | runtime type checking is enabled but no exception will be raised |
| SEVERITY_LEVEL.DISABLED | type checking will be ignored |

- The default level is `SEVERITY_LEVEL.ENABLED`
```python
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing import match_typing

@match_typing
def a(value: int):
    return value * 2

a(2) == 4  # this will raise a TypeMisMatch-Exception
```

- the `Warning` behavior `SEVERITY_LEVEL.WARNING`
```python
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing import match_typing

@match_typing(severity=SEVERITY_LEVEL.WARNING)
def a(value: int):
    return value * 2

a('2')  # "Incorrect parameters: value: <class 'int'>"
# this is the output you will see in your logs and no Exception will be raised
```

- the `Disabled` behavior `SEVERITY_LEVEL.DISABLED`
```python
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing import match_typing

@match_typing(severity=SEVERITY_LEVEL.DISABLED)
def a(value: int):
    return value * 2

a(2)  # 4
a('2')  # '22'
```

- The `match_class_typing` decorator works in exactly the same way:
```python
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing import match_class_typing

@match_class_typing(severity=SEVERITY_LEVEL.WARNING)
class Dummy:
    attr = 100

    def a(self, val: int):
        return val * 3

    def b(self):
        return 'b'

d = Dummy()
d.a('2')  # in the logs "Incorrect parameters: val: <class 'int'>"


@match_class_typing(severity=SEVERITY_LEVEL.DISABLED)
class Dummy:
    attr = 100

    def a(self, val: int):
        return val * 3

    def b(self):
        return 'b'

d = Dummy()
d.a('2')  # '222'
```

### SEVERITY_LEVEL as environment variable

- To make things easier you can set the `SEVERITY_LEVEL` as an enviroment variable.
  
- Just use the helper function `set_severity_level`:
```python
# call this somewhere in your code
from strongtyping.config import SEVERITY_LEVEL, set_severity_level

set_severity_level(SEVERITY_LEVEL.ENABLED)
set_severity_level(SEVERITY_LEVEL.WARNING)
set_severity_level(SEVERITY_LEVEL.DISABLED)
```

- Or you can set the environment value `ST_SEVERITY` directly:
```python
environ['ST_SEVERITY'] = 1  # enabled
environ['ST_SEVERITY'] = 2  # warning
environ['ST_SEVERITY'] = 0  # disabled
```
