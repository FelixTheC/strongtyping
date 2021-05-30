# IterValidator type
- The `IterValidator` type is like `Union` and `map` you can join a type-hint and a validation function.
- The function you pass as the second argument will be called with each element inside of the argument.
- These works only when using with `match_typing`.
- If the check fails it will raise a `TypeMisMatch` or the Exception you specify in `@match_typing(excep_raise=<SomeException>)`

### Usage
- The first parameter of the `IterValidator` must be the `type` you're requiring
- The second parameter of the `IterValidator` must be a `function`
- Should __only__ be used __with__ `iterables`
```
Validator[<type>, <function>]
```
---
### Example code

```python
import pytest
import typing
import unittest
from unittest import TestCase
import decimal
import fractions

from strongtyping.strong_typing import match_typing
from strongtyping.types import IterValidator, Validator

number = typing.Union[str, int, float, fractions.Fraction, decimal.Decimal]


def allow_only_int_convertible(value: number):
    if isinstance(value, str):
        if not value.isdigit():
            raise TypeError
        else:
            value = int(value)

    if not value % 1 == 0:
        raise TypeError
    return True


AllowedCluster = IterValidator[typing.Iterable[number], allow_only_int_convertible]


@match_typing(excep_raise=TypeError)
def cluster(items: AllowedCluster):
    return True


assert cluster((1, 2, 3, 4, 5, 5, 7, "7"))
assert cluster([1, 2, decimal.Decimal("3")])
assert cluster([1, 2, fractions.Fraction(3, 1)])

with pytest.raises(TypeError):
    cluster([1, 2, "abc"])
    cluster([1, 2, decimal.Decimal("2.1")])
    cluster([1, 2, fractions.Fraction(3, 2)])
```