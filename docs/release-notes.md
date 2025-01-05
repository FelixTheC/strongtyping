# Release Notes

## v3.13.1

### Enhancements

- Updated the CI workflow to use Python 3.13 and modernized the build process by replacing deprecated setup.py commands with build and twine.
- Adjusted pyproject.toml to align with new packaging configurations.
- Enabled Python 3.13 in GitHub Actions workflows and tests, adding related compatibility checks where necessary.
- Upgraded actions/checkout and adjusted test markers for feature-specific availability in 3.13.
- Replaced all occurrences of "TypeMisMatch" with the correct term "TypeMismatch" across documentation files, improving consistency and correctness in the error type mentioned throughout the project.

### New Features

- Added support for Python version 3.13 as reflected in the README updates. Now users are aware of the extended compatibility with newer Python versions.

### Refactoring

- Relocated all test files from strongtyping/tests to a root-level tests directory for better project organization and consistency. No code changes were made, ensuring functionality remains unaffected.

## v3.12.1

### Enhancement

- feat: raise UndefinedKey exception on user decision by @FelixTheC in #130
  - new exception type UndefinedKey
  - new allowed parameter(throw_on_undefined) for match_class_typing which will be thrown if you try to init a TypeDict with an unspecified attribute/key

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
- better `TypeMismatch` tracecback informations (you will now see the value which caused this issue)

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