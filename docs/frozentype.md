# Frozentype
- Beta feature
- assigning a class attribute to be a Frozentype will prevent from changing the current type by accident 
this means an `int` or a `dict` typed attribute cannot be changed anymore

### Usage
```python
from strongtyping.types import FrozenType

class A:
    foo = FrozenType(int)

obj_a = A()

# will raise following an error
obj_a.foo = "1"  
# TypeError: `This` is a final type. 
# 	You cannot assign <class 'str'> to <class 'int'>
```
