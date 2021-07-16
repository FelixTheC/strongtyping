## docs_from_typing

- Wth `class_docs_from_typing` you can generate a docstring from your type annotations for a whole class
  
- Inside the docstring there will be extra information indicating whether a parameter is an `Argument` 
  a `Positional Only Argument` or a `Keyword Argument`
- Default values are also shown
- Existing docstrings will not be overwritten

### Usage
- add `class_docs_from_typing` as decorator to your class
- the default docstring rendering style is `reST` you can also use `numpy` by setting `doc_type` to `numpy`
    - `@class_docs_from_typing(doc_type="numpy")`

### Examples
```python
from strongtyping.docs_from_typing import class_docs_from_typing


@class_docs_from_typing
class Vehicle:
    """The Vehicle object contains lots of vehicles"""

    def __init__(self, arg: str, *args, **kwargs):
        """
        $2 at least one value of type string is needed
        """
        self.arg = arg

    def cars(self, distance: int, destination: str):
        """We can't travel a certain distance in vehicles without fuels, so here's the fuels"""
        pass

    def fuel(self, fuel):
        """Some text"""
        pass

>>> help(Vehicle)
Help on class Vehicle in module __main__:

class Vehicle(builtins.object)
 |  Vehicle(arg: str, *args, **kwargs)
 |  
 |  The Vehicle object contains lots of vehicles
 |  
 |  :param arg: argument 
 |  :param args: variadic arguments 
 |          at least one value of type string is needed
 |  :param kwargs: variadic keyword arguments 
 |  :type arg: str
 |  :type args: tuple
 |  :type kwargs: dict
 |  
 |  Methods defined here:
 |  
 |  __init__(self, arg: str, *args, **kwargs)
 |  
 |  cars(self, distance: int, destination: str)
 |      We can't travel a certain distance in vehicles without fuels, so here's the fuels
 |      
 |      :param distance: argument 
 |      :param destination: argument 
 |      :type distance: int
 |      :type destination: str
 |  
 |  fuel(self, fuel)
 |      Some text
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  __dict__
 |      dictionary for instance variables (if defined)
 |  
 |  __weakref__
 |      list of weak references to the object (if defined)
```

#### Existing docs_from_typing decorators won't be overwritten
```python
from strongtyping.docs_from_typing import class_docs_from_typing, numpy_docs_from_typing


@class_docs_from_typing(doc_type="numpy")
class Vehicle:
    """The Vehicle object contains lots of vehicles"""

    def __init__(self, arg: str, *args, **kwargs):
        """
        $2 at least one value of type string is needed
        """
        self.arg = arg

    @numpy_docs_from_typing(insert_at="___")
    def cars(self, distance: int, destination: str):
        """
        We can't travel a certain distance in vehicles without fuels, so here's the fuels
        ___

        Some more useful information about this function
        there are a lot of useful information for this small function
        and why it
        Returns
        -------
        Unicorn
        """
        pass

    def fuel(self, fuel):
        """Some text"""
        pass

>>> help(Vehicle)
Help on class Vehicle in module __main__:

class Vehicle(builtins.object)
 |  Vehicle(arg: str, *args, **kwargs)
 |  
 |  The Vehicle object contains lots of vehicles
 |  
 |  Parameters
 |  ----------
 |  arg : argument of type str
 |  args : variadic arguments of type tuple
 |          at least one value of type string is needed
 |  kwargs : variadic keyword arguments of type dict
 |  
 |  Methods defined here:
 |  
 |  __init__(self, arg: str, *args, **kwargs)
 |  
 |  cars(self, distance: int, destination: str)
 |      We can't travel a certain distance in vehicles without fuels, so here's the fuels
 |      
 |      Parameters
 |      ----------
 |      distance : argument of type int
 |      destination : argument of type str
 |      
 |      Some more useful information about this function
 |      there are a lot of useful information for this small function
 |      and why it
 |      Returns
 |      -------
 |      Unicorn
 |  
 |  fuel(self, fuel)
 |      Some text
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  __dict__
 |      dictionary for instance variables (if defined)
 |  
 |  __weakref__
 |      list of weak references to the object (if defined)
```
