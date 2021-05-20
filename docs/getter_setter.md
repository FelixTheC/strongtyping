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