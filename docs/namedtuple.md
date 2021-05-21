## typed_namedtuple

- __typed_namedtuple is only available from python >= 3.8__
- from my side it was only logical to create an own version of namedtuple with typing support

Here are some examples of how you can use it.
```python
from strongtyping.type_namedtuple import typed_namedtuple

Dummy = typed_namedtuple('Dummy', 'spell:str, mana:int or str,effect:list')

Dummy(mana='Lumos', spell=5, effect='Makes light')  # will raise a TypeError
Dummy(spell='Lumos', mana=5, effect=['Makes light', ])  # works like a charm

```
- the same happens also with wrong default values (the typed_namedtuple needs the exact same length)
```python
from strongtyping.type_namedtuple import typed_namedtuple

# will raise a TypeError
Dummy = typed_namedtuple('Dummy', ['spell:str', 'mana:int', 'effect:list'],  defaults=[0, '', ''])

```
- and also when you try to replace an attribute with a wrong type
```python
from strongtyping.type_namedtuple import typed_namedtuple
Dummy = typed_namedtuple('Dummy', ['spell:str', 'mana:int', 'effect:list'])
d = Dummy('Lumos', mana=5, effect=['Makes light', ])

d._replace(effect=b'Makes light')  # will raise a TypeError

```

- it is also possible to use the typing.NamedTuple way for instantiating
```python
from strongtyping.type_namedtuple import typed_namedtuple
Dummy = typed_namedtuple('Dummy', [('spell', str), ('mana', int), ('effect', Union[list, tuple])])

Dummy('Papyrus Reparo', 10, {1, 2, 3})  # will raise a TypeError

# when using this way you will also have the __annototaions__

print(Dummy.__annotations__)
# {'spell': <class 'str'>, 'mana': <class 'int'>, 'effect': typing.Union[list, tuple]}

```

- the docstring will also display the types of the parameter in the reST-style
```python
from strongtyping.type_namedtuple import typed_namedtuple
Dummy = typed_namedtuple('Dummy', 'spell:str, mana:int or str,effect:list')

print(help(Dummy))

"""
class Dummy(builtins.tuple)
     |  Dummy(*args, **kwargs)
     |  
     |  Dummy(spell, mana, effect)
     |  :type spell: str
     |  :type mana: int or str
     |  :type effect: list
    ...
"""
```
