# Strong Typing
<p>Decorator which checks whether the function is called with the correct type of parameters.<br> 
And <b><em>raises</em> TypeMisMatch</b> if the used parameters in a function call where invalid.</p>
 
<p>See _test_typing.py_ for more informations.<br>
But why??</p>

> I really love python and his freedom but with the new option of adding type hints I wanted to get rid of writing `if isinstance(value, whatever)` in my programs. 
> 
> In a bigger project it happened that some developers used a really tiny IDE 
  and others a more advanced one which highlighted typing issues. And there the trouble began, we had a bug and after a longer
  debugging session we found out that the issue was a wrong type of an argument, 
  it doesn't crashed the program but the output was totally not what we expected. 
> 
> And this is the reason why I created this package.


## Getting Started
As normal decorator
```
@match_typing
def foo_bar(a: str, b: int, c: list):
    ...
```
as class method decorator
```
class Foo:
    ...
    @match_typing
    def foo_bar(self, a: int):
        ...
```
You can also use a mix of typed and untyped parameters but then only the typed parameters are check on runtime
```
@match_typing
def foo_bar(with_type_a: str, without_type_a, with_type_b: list, without_type_b):
    ...

# no exception
foo_bar('hello', 'world', [1, 2, 3], ('a', 'b'))

# will raise an exception
foo_bar(123, 'world', [1, 2, 3], ('a', 'b'))
```

It is also possibile to add you own exception
```
@match_typing(excep_raise=SomeException)
def foo_bar(with_type_a: str, without_type_a, with_type_b: list, without_type_b):
    ...
```

And last but not least you can also enable internal cache with cache_size = 1
```
@match_typing(cache_size=1)
def foo_bar(a: tuple, b: MyClass):
    ...
```

At the current state it will work with

- builtin types like: str, int, tuple etc
- from typing: 
    - List
    - Tuple
    - Union also nested ( Tuple[Union[str, int], Union[list, tuple]] )
    - Any
    - Dict
    - Set
    - Type
    - Iterator
    - Callable
- with string types representation like
```
class A:
    @match_typing
    def func_a(self, a: 'A'):
```

### Tested for Versions
- 3.6, 3.7, 3.8
### Prerequisites
- pytest

### Installing
- pip install strongtyping
- pip install git+https://github.com/FelixTheC/strongtyping.git

### Running the tests
- python test_typing.py

#### Versioning
- For the versions available, see the tags on this repository.

### Authors
- Felix Eisenmenger - Initial work

### License
- This project is licensed under the MIT License - see the LICENSE.md file for details

### Special thanks
- Thanks to Ruud van der Ham for helping me improve my code
- And all how gave me Feedback in the Pythonista Cafe
