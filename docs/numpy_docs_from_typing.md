## numpy_docs_from_typing

- Wth `numpy_docs_from_typing` you can generate a docstring from your type annotations
  
- Inside the docstring there will be extra information indicating whether a parameter is an `Argument` 
  a `Positional Only Argument` or a `Keyword Argument`
- Default values are also shown

- Existing docstrings will not be overwritten
```python
from typing import Union, Literal, Dict

from strongtyping.docs_from_typing import numpy_docs_from_typing

@numpy_docs_from_typing
def foo(val_a: Literal['foo', 'bar'], 
        val_b: Dict[str, Union[int, float]],
        val_c: str = "Hello World") -> Dict[str, Union[int, float]]:
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
    """

>>>print(foo.__doc__)

Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

Parameters
----------
val_a : argument of type `str` allowed values are `foo` or `bar`
val_b : argument of type Dict(str, int or float)
val_c : argument of type str
	Default is Hello World

Returns
-------
Dict(str, int or float)

```

- with $<1-9> you can assign specific infos to each parameter
```python
from typing import List

from strongtyping.docs_from_typing import numpy_docs_from_typing

@numpy_docs_from_typing(remove_linebreak=True)
def foo(val_a: int, val_b: List[int]) -> List[str]:
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

Parameters
----------
val_a : argument of type int
	Lorem ipsum dolor sit amet
val_b : argument of type List(int)
	nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
	sed diam voluptua

Returns
-------
List(str)

```

- with `linebreak=True` you can remove the linebreak between the first paragraph and the beginning of the parameters
```python
from typing import List

from strongtyping.docs_from_typing import numpy_docs_from_typing

@numpy_docs_from_typing(remove_linebreak=True)
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

Parameters
----------
val_a : argument of type int
	Lorem ipsum dolor sit amet
val_b : argument of type List(int)
	nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat,
	sed diam voluptua
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
    
    Returns
    -------
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
    """

>>>print(foo.__doc__)

Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam


Parameters
----------
val_a : argument of type int
val_b : argument of type List(int)

Returns
-------
Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

```

### TypedDict
- when used with a `TypedDict` the fields of the `TypedDict` are included
```python
class MyDict(TypedDict):
    sales: int
    country: str
    product_codes: List[str]

    
@numpy_docs_from_typing
def foo(val: MyDict, val_b: List[int]) -> str:
    ...

>>>print(foo.__doc__)

Lorem ipsum dolor samit
Parameters
----------
val : argument of type MyDict[TypedDict] required fields are 
	`{'sales': 'int', 'country': 'str', 'product_codes': 'List(str)'}`
val_b : argument of type List(int)

Returns
-------
str
```
- when setting `total=False` the `required` word in the doc string will be removed
```python
class MyDict(TypedDict, total=False):
    sales: int
    country: str
    product_codes: List[str]

    
@numpy_docs_from_typing
def foo(val: MyDict, val_b: List[int]) -> str:
    ...

>>>print(foo.__doc__)
Lorem ipsum dolor samit
Parameters
----------
val : argument of type MyDict[TypedDict] fields are 
	`{'sales': 'int', 'country': 'str', 'product_codes': 'List(str)'}`
val_b : argument of type List(int)

Returns
-------
str
```
