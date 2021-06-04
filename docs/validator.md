# Validator type
- The `Validator` type is like Union you can join a type-hint and a validation function.
- These works only when using with `match_typing`.
- If the Validation fails then you will receive a `ValidationError` if the type doesn't match 
  then you will receive a `TypeMisMatch`

### Usage
- The first parameter of the `Validator` must be the `type` you're requiring
- The second parameter of the `Validator` must be a `function`
```
Validator[<type>, <function>]
```
- A `TypeError` will be raised if the parameters are not in the correct order
---

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


### TypedDict
- Works also with the `Validator` type
```python
from typing import List, TypedDict

from strongtyping.strong_typing import match_class_typing, match_typing
from strongtyping.types import Validator

@match_class_typing
class MyDict(TypedDict, total=False):
    sales: int
    country: str
    product_codes: List[str]

def allow_only_valid_country_names(value: MyDict):
    return not value.get("country", "").isnumeric()

AllowedDicts = Validator[MyDict, allow_only_valid_country_names]

@match_typing
def cluster(val: AllowedDicts):
    return True

# works like expected
cluster({"sales": 10, "country": "Europe", "product_codes": "Hello World".split()})
cluster({"sales": 10, "product_codes": "Hello World".split()})

# will raise a ValidationError
cluster({"sales": 10, "country": "123456789", "product_codes": "Hello World".split()})
cluster({"country": "123456789", "product_codes": "Hello World".split()})

# will raise a TypeMisMatch
cluster({"sales": 10, "country": "Europe", "product_codes": list(range(10))})
cluster({"sales": "10", "country": "Europe"})
cluster({"product_codes": list(range(10))})
```


## ValidationError traceback
- A traceback for the `Validator` can look similar to this
```
Argument: `{2: [2, 4]}` did not passed the validation defined here 
	File: "/home/eisenmenger/PycharmProjects/strongtyping/strongtyping/tmp.py", line: 13
	Name: min_length
```
- `File:` describes where the validation function is defined
- `Name:` the name of the validation function