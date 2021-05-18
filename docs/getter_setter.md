## setter
this decorator can replace your *@foo.setter* from property and check your typing
- this is an extension of [easy_property](https://github.com/salabim/easy_property)
```python
from strongtyping.strong_typing import getter
from strongtyping.strong_typing import setter

class Dummy:
    attr = 100
    val = 'foo'

    @getter
    def b(self):
        return self.val

    @setter
    def b(self, val: str):
        self.val = val

d = Dummy()
d.b == 'foo'  # will raise AttributeError 

d.b = 'bar'  # works like a charm

d.b = 1  # will raise TypeMisMatch
```
- [Back to top](#strong-typing)

## getter_setter
this decorator can replace *@propery* from property and check your typing
- this is an extension of [easy_property](https://github.com/salabim/easy_property)
```python
from strongtyping.strong_typing import getter_setter

class Dummy:
    attr = 100

    @getter_setter  # here you will have all in one place (DRY) 
    def c(self, val: int = None):
        if val is not None:
            self.attr = val
        return self.attr

d = Dummy()
d.c == 100  # works like a charm

d.c = 1  # works like a charm

d.c = 'foobar'  # will raise TypeMisMatch
```