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


### Prerequisites
- pytest

### Installing
- python setup.py install
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
