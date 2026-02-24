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
- Single class methods inside of a previously decorated class can be overwritten with the `@match_typing` decorator:
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

### with dataclass
- The `match_class_typing` decorator will also work very well with `dataclass`

```python
from dataclasses import dataclass
from strongtyping.strong_typing import match_class_typing

# normal usage

@dataclass
class Dummy:
    attr_a: int
    attr_b: str

# no error will happen here
d = Dummy("10", 10)

# so we switched the types of the values unnoticed
assert d.attr_a == "10"
assert d.attr_b == 10


# with the `match_class_typing` decorator this won't happen anymore

@match_class_typing
@dataclass
class Dummy:
    attr_a: int
    attr_b: str

# wrong types are raising a TypeMismatch error
assert Dummy("10", 10)
```

### with TypedDict
- The `match_class_typing` decorator will also work very well with `TypedDict`
```python
from typing import List, TypedDict

from strongtyping.strong_typing import match_class_typing


@match_class_typing
class SalesSummary(TypedDict):
    sales: int
    country: str
    product_codes: List[str]

# works like expected
SalesSummary({"sales": 10, "country": "Foo", "product_codes": ["1", "2", "3"]})

# will raise a TypeMismatch
SalesSummary({"sales": "Foo", "country": 10, "product_codes": [1, 2, 3]})
```
- The `total` keyword will supported like the original TypeDict
```python
from typing import List, TypedDict

from strongtyping.strong_typing import match_class_typing


@match_class_typing
class SalesSummary(TypedDict, total=False):
    sales: int
    country: str
    product_codes: List[str]

# works like expected
SalesSummary({"sales": 10, "product_codes": ["1", "2", "3"]})

# will raise TypeMismatch
SalesSummary({"sales": "Foo", "product_codes": [1, 2, 3]})
```
- `match_class_typing` supports a special parameter when used with __TypedDict__: `throw_on_undefined`
- this will raise an `UndefinedKey` exception when a key is not defined in the __TypedDict__
```python
from typing import List, TypedDict
from strongtyping.strong_typing import match_class_typing
from strongtyping.strong_typing_utils import UndefinedKey

@match_class_typing(throw_on_undefined=True)
class User(TypedDict):
    id: str
    username: str
    description: str | None

# works like expected
User({"id": "0123", "username": "test", "description": None})

# will throw `UndefinedKey`
User({"id": "0123", "username": "test", "description": None, "age": 10})
```
#### make TypedDict a bit stricter
- you can use the `match_class_typing` decorator with the `Validator` type to make the TypedDict a bit stricter

```python
import uuid
from typing import List, TypedDict
from strongtyping.strong_typing import match_class_typing
from strongtyping.st_types import Validator


def is_convertible_to_uuid(x: str) -> bool:
    try:
        uuid.UUID(x)
    except ValueError:
        return False
    return True


@match_class_typing
class User(TypedDict):
    id: Validator[str, lambda x: is_convertible_to_uuid(x)]
    username: Validator[str, lambda x: 10 <= len(x) >= 15]
    description: str | None


# will throw `ValidationError`
User({"id": "0123", "username": "loremipsum", "description": None})

# is valid
User({"id": "63f24361-57cc-42b2-9310-06af5bd3eff4",
      "username": "loremipsumdolor",
      "description": None})
```
- for an easier usage you can use the function `validate_typed_dict` from `strongtyping.helpers`

```python
from strongtyping.helpers import validate_typed_dict
from strongtyping.st_types import Validator

example_request_data = {
    "id": "63f24361-57cc-42b2-9310-06af5bd3eff4",
    "username": "loremipsumdolor",
    "description": None,
}

if validate_typed_dict(User, example_request_data):
# do something with the data
else:
# handle the error
```
