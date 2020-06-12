# Strong Typing
<p>Decorator which <b>checks at Runtime</b> whether the function is called with the correct type of parameters.<br> 
And <b><em>raises</em> TypeMisMatch</b> if the used parameters in a function call where invalid.</p>
 
###The problem:
```
def multipler(a: int, b: int):
    return a * b


product = multipler(3, 4)
# >>> 12

# Some IDE's will/can highlight that one of the parameter doesn't match but you can run it
product_2 = multipler('Hello', 'World')
# >>> TypeError
# When we receiver an Exception then we are ‘safe’ and know what to do 
# but sometimes we will not run into an Exception

product_3 = multipler('Hello', 4)
# >>> 'HelloHelloHelloHello'
# No Exception but the result isn’t really what we expect
```
> Now we can say that we will check the types in the function body to prevent this.

```
def multipler(a: int, b: int):
    if isinstance(a, int) and isinstance(b, int):
        return a * b
    ...
```
> But when your function needs a lot of different parameters with different types you have to create a lot of noising code.
>
> And why should we then use typing in our parameters??

###My solution:
<p>I created a decorator called <b>@match_typing</b> which will check at runtime if the parameters you used when calling this function are from the same type as you wanted.</p>
Here are some examples from my tests

    @match_typing
    def func_a(a: str, b: int, c: list):
        ...
    
    func_a('1', 2, [i for i in range(5)])
    # >>> True
    
    func_a(1, 2, [i for i in range(5)])
    # >>> will raise a TypeMismatch Exception
    
    @match_typing
    def func_e(a: List[Union[str, int]], b: List[Union[str, int, tuple]]):
        return f'{len(a)}-{len(b)}'

    func_e([1, '2', 3, '4'], [5, ('a', 'b'), '10'])
    # >>> '4-3'
    
    func_e([5, ('a', 'b'), '10'], [1, '2', 3, datetime.date])
    # >>> will raise a TypeMismatch Exception
    
> I really love python and his freedom but with the new option of adding type hints I wanted to get rid of writing `if isinstance(value, whatever)` in my programs. 
> 
>> In a bigger project it happened that some developers used a really tiny IDE 
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
You can also use a mix of typed and untyped parameters but then only the typed parameters are checked on runtime
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
