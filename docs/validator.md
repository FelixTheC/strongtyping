# Validator type
- The `Validator` type is like Union you can join a type-hint and a validation function.
- These works only when using with `match_typing`.
- If the Validation fails then you will receive a `ValidationError` if the type doesn't match 
  then you will receive a `TypeMisMatch`
  
#### lambda expression
```python
from strongtyping.strong_typing_utils import Validator
from strongtyping.strong_typing import match_typing

@match_typing
def foo(val_a: Validator[list, lambda x: len(x) > 2]):
  return True

assert foo([1, 2, 3])
assert foo([1, 2])  # raises a ValidationError
assert foo({1, 2, 3})  # raises TypeMisMatch
```

#### normal function
```python
from functools import partial
from typing import Dict, List, Tuple, Union

from strongtyping.strong_typing_utils import Validator
from strongtyping.strong_typing import match_typing

def min_length(val):
  return len(val) > 2

@match_typing
def foo(val_a: Validator[List[int], min_length]):
    return True


assert foo([1, 2, 3])
assert foo([1, 2])  # ValidationError
assert foo([1, ])  # ValidationError
assert foo(['1', '2', '3'])  # TypeMisMatch
assert foo((1, 2, 3))  # TypeMisMatch
```


#### partial function
```python
from functools import partial
from typing import Dict, List, Tuple, Union

from strongtyping.strong_typing_utils import Validator
from strongtyping.strong_typing import match_typing


def min_length(val, *, size):
  return len(val) >= size


@match_typing
def foo(val_a: Validator[dict[Union[str, int], Union[list[int], tuple[int, ...]]], partial(min_length, size=2)]):
  return True


assert foo({2: [2, 4], 'hello': (2, 3, 4, 5)})
assert foo({2: [2, 4]})  # ValidationError
assert foo(((1, 2), (3, 4)))  # TypeMisMatch
```

## ValidationError traceback
- A traceback for the `Validator` can look similar to this
```
Argument: `{2: [2, 4]}` did not passed the validation defined here 
	File: /strongtyping/tests/test_validator_type.py
	Name: min_length
	Line: 56 - 58
```
