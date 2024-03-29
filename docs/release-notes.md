# Release Notes

## v2.1.9
- improvement of callable checks
  ```python
  # the parameter/return value is an unknown callable
  Callable[..., Any]
  ```
  ```python
  # the callable will have no arguments and returns a string
  Callable[[], str]
  ```
  ```python
  # the annotation needs to match the callable you want to allow
  # for multiple options use
  Union[
        Callable[[int, str, str], str], 
        Callable[[int, str, int], str]
       ]
  ```

## v2.1.8
- fix `isinstance` with `@match_class_typing` decorator

## v2.1.7
- feat `FinalClass` decorator, __disable Inheritance__ for the decorated class
- fix bug #71 (Initializing TypedDict like a normal class with kwargs fails)
- fix bug #69 (Handle functions wich specify a value having of type TypeDict)

## v2.1.6
- class decorator for docstrings from typing `class_docs_from_typing`
- beta feature FrozenType

## v2.1.5
- support for latest strongtyping-modules version (0.1.4)
- support for TypedDict
- bugfixes

## v2.1.4
- fix `IterValidator` with typing.Any

## v2.1.3
- moving `Validator` to `strongtyping.types`
- fixing some bugs
- new type `IterValidator` which works mostly like map

## v2.1.2
- include missing type check for `Iterable`

## v2.1.0
- new type hint type `Validator` like `Union` you join a type-hint and a validation function
- better `TypeMisMatch` tracecback informations (you will now see the value which caused this issue)

## v2.0.2
- correct handling for empty containers and empty type-hints like List instead of list

## v2.0.1
- Better return type value formatting in rest_docs_from_typing, numpy_docs_from_typing

## v2.0.0
- Added two new decorators which can create docstrings from type informations.
    - rest_docs_from_typing
    - numpy_docs_from_typing
- Improvement of Documentation
- Moved docs from a simple README.md to readthedocs.com

## v1.7.0
- Code improvements
- bug fixes