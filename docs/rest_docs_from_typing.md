## rest_docs_from_typing

- With `rest_docs_from_typing` you can generate a docstring from your type annotations
  
- Inside of the docstring there will be addition information indicating whether the parameter is an `Argument` 
  a `Positional Only Argument` or a `Keyword Argument`
- Default values are shown:
```python
from typing import List

from strongtyping.docs_from_typing import rest_docs_from_typing

@rest_docs_from_typing
def foo(val_a: int, val_b: List[int]):
    pass

>>>print(foo.__doc__)

Function foo


:param val_a: argument 
:param val_b: argument 
:type val_a: int
:type val_b: List(int)
```

- Existing docstrings will not be overwritten:
```python
from typing import List

from strongtyping.docs_from_typing import rest_docs_from_typing

@rest_docs_from_typing
def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, 
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
    """

>>>print(foo.__doc__)

Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

:param val_a: argument 
:param val_b: argument 
:type val_a: int
:type val_b: List(int)

```

- Using `$<1-9>` you can assign specific information to each parameter:
```python
from typing import List

from strongtyping.docs_from_typing import rest_docs_from_typing

@rest_docs_from_typing
def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

    $1 Lorem ipsum dolor sit amet
    $2 nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
    sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
    Stet clita kasd gubergren,
    """

>>>print(foo.__doc__)

Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam


:param val_a: argument 
	Lorem ipsum dolor sit amet
:param val_b: argument 
	nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
	sed diam voluptua
:type val_a: int
:type val_b: List(int)

```
- with `linebreak=True` you can remove the linebreak between the first paragraph and the beginning of the parameters

```python
from typing import List

from strongtyping.docs_from_typing import rest_docs_from_typing

@rest_docs_from_typing(remove_linebreak=True)
def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

    $1 Lorem ipsum dolor sit amet
    $2 nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
    sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
    Stet clita kasd gubergren,
    """

>>>print(foo.__doc__)

Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

:param val_a: argument 
	Lorem ipsum dolor sit amet
:param val_b: argument 
	nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
	sed diam voluptua
:type val_a: int
:type val_b: List(int)
```

- with `insert_at` you can define a placeholder where you want to place the generated docstring
```python
from typing import List

from strongtyping.docs_from_typing import numpy_docs_from_typing

@numpy_docs_from_typing(insert_at='---')
def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
    
    ---
    raises: IndexError
    
>>>print(foo.__doc__)

Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

:param val_a: argument 
	Lorem ipsum dolor sit amet
:param val_b: argument 
	nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
	sed diam voluptua
:type val_a: int
:type val_b: List(int)
raises: IndexError
```
