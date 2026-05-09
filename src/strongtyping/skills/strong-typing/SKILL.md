---
name: strong-typing
description: Enforce runtime type safety using the strongtyping library. Use this skill when you want to add runtime type checking to functions, methods, or classes, or when debugging type-related issues in a project that uses strongtyping.
---

# Strongtyping Agent Skill

`strongtyping` is a library that provides decorators for runtime type checking in Python. It uses Python type hints to
validate function arguments and return values.

## Core Features

### 1. `@match_typing`

Use this decorator on functions or methods to enforce type checking on their parameters.

```python
from strongtyping.strong_typing import match_typing


@match_typing
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age} years old."
```

**Key Parameters:**

- `excep_raise`: The exception to raise on mismatch (default: `TypeMismatch`).
- `severity`: Control whether to raise an exception or a warning (default: `"env"`, which follows the
  `ST_SEVERITY` environment variable).
- `allow_duck_typing`: If `True`, allows duck typing for protocol-like checks.
- `validate_return`: If `True`, also validates the return value.

### 2. `@match_class_typing`

Use this decorator on a class to automatically apply `@match_typing` to all its methods (including `__init__`).

```python
from strongtyping.strong_typing import match_class_typing


@match_class_typing
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

### 3. Validation with `Annotated`

The modern way to add custom validation logic. Any callable in `Annotated` metadata will be executed.

```python
from typing import Annotated
from strongtyping.strong_typing import match_typing


def is_positive(value: int) -> bool:
    return value > 0


@match_typing
def process(x: Annotated[int, is_positive]):
    return f"Processed {x}"
```

**Predefined Validators (`strongtyping.helpers`):**

- `Gt(v)`, `Gte(v)`, `Lt(v)`, `Lte(v)`: Comparison checks.
- `Range(min, max)`: Range check.
- `Len(lower=None, upper=None)`: Length check for strings or collections.
- `Regex(pattern)`: Regex match for strings.
- `IsPositive()`, `IsNegative()`, `IsUUID()`: Common type-specific checks.

### 4. `MatchTypedDict`

Validate data against a `TypedDict`. Useful for JSON payloads.

```python
from typing import TypedDict
from strongtyping.strong_typing import MatchTypedDict


class UserData(TypedDict):
    name: str
    age: int


data = {"name": "Alice", "age": "30"}
MatchTypedDict(UserData)(data)  # Raises TypeMismatch
```

### 5. `typed_namedtuple`

A type-safe version of `collections.namedtuple`.

```python
from strongtyping.type_namedtuple import typed_namedtuple

User = typed_namedtuple('User', 'name:str, age:int')
u = User(name='Alice', age='30')  # Raises TypeError
```

### 6. Property Decorators

Combine property behavior with runtime type checking.

```python
from strongtyping.strong_typing import getter_setter


class Circle:
    def __init__(self, radius: int):
        self._radius = radius

    @getter_setter
    def radius(self, val: int = None):
        if val is not None:
            self._radius = val
        return self._radius
```

### 7. `FinalClass` & `FrozenType`

- `@FinalClass`: Prevent class inheritance.
- `FrozenType(type)`: Prevent attribute type changes (beta).

```python
from strongtyping.st_types import FrozenType


class A:
    foo = FrozenType(int)


obj = A()
obj.foo = "1"  # Raises TypeError
```

### 8. Documentation Enhancers

Automatically generate docstrings from type hints.

- `@class_docs_from_typing`: Apply to a class.
- `@rest_docs_from_typing` / `@numpy_docs_from_typing`: Apply to individual methods.

```python
from strongtyping.docs_from_typing import class_docs_from_typing


@class_docs_from_typing
class MyClass:
    def __init__(self, val: int):
        self.val = val
```

## When to use this skill

- When you want to ensure that a function's arguments match their type hints at runtime.
- When you need to enforce complex validation (range, regex, length) using `Annotated` and `strongtyping.helpers`.
- When you are dealing with external data (API responses, user input) and want to validate it against a `TypedDict`.
- When you want to ensure class properties are type-safe using `@getter_setter`.
- When you want to prevent inheritance of specific classes or accidental type changes of attributes.
- When you want to automatically generate docstrings (reST or numpy style) from type annotations.
- When debugging "AttributeError" or "TypeError" that might be caused by incorrect types being passed around.

## Best Practices

- **Type Annotations**: `strongtyping` relies on standard Python type hints. Ensure they are present and accurate.
- **Performance**: Runtime checks have a cost. Use them strategically at the entry points of your application or for
  critical logic. Note that since version 3.13.6, `strongtyping` is compiled with `mypyc` for a ~5x performance boost.
- **Exception Handling**: Catch `TypeMismatch` or `ValidationError` from `strongtyping.exceptions` to handle validation
  errors gracefully.
- **Annotated vs Validator**: Use `Annotated` for new code, as the `Validator` type is deprecated.
