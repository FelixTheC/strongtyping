from _typeshed import Incomplete
from strongtyping.docstring_typing import check_doc_str_type as check_doc_str_type
from strongtyping.strong_typing import check_type as check_type, match_typing as match_typing
from typing import List, Tuple, Union

use_match_typing: Incomplete

def typed_namedtuple(typename: str, field_names: Union[List[str], str, List[Tuple[str, object]]], *, rename: bool = ..., defaults: Union[list, tuple] = ..., module: str = ...): ...
