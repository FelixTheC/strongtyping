## setter
This decorator can replace your `@foo.setter` and check your typing at the same time.
- It's an extension of [easy_property](https://github.com/salabim/easy_property)
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
