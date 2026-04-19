# Annotated for validation

You can use `typing.Annotated` to add validation logic to your type hints. Any callable in the metadata will be executed
with the parameter value.

```python
from typing import Annotated
from strongtyping.strong_typing import match_typing


def is_positive(value: int) -> bool:
    return value > 0


@match_typing
def process(x: Annotated[int, is_positive]):
    return f"Processed {x}"


process(10)  # Works
process(-5)  # Raises TypeMismatch
```

Multiple validators can be used:

```python
from typing import Annotated
from strongtyping.strong_typing import match_typing

@match_typing
def process(x: Annotated[int, lambda x: x > 0, lambda x: x % 2 == 0]):
    ...
```

## Predefined validators

### `from strongtyping.helpers import *`

- `Gt`
    - `Annotated[int, Gt(18)]`
- `Gte`
    - `Annotated[int, Gte(18)]`
- `Lt`
    - `Annotated[int, Lt(18)]`
- `Lte`
    - `Annotated[int, Lte(18)]`
- `Range`
    - `Annotated[int, Range(18, 30)]`
- `IsPositive`
    - `Annotated[int, IsPositive()]`
- `IsNegative`
    - `Annotated[int, IsNegative()]`
- `IsUUID`
    - `Annotated[str, IsUUID()]`
- `Len`
    - `Annotated[str, Len(lower=3)]`
    - `Annotated[str, Len(lower=3, upper=20)]`
- `Regex`
    - `Annotated[str, Regex(r'/w*')]`