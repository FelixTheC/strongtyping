# Release Notes

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