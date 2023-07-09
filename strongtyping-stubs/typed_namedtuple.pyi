from _typeshed import Incomplete
from strongtyping.docstring_typing import check_doc_str_type as check_doc_str_type
from strongtyping.strong_typing import check_type as check_type, match_typing as match_typing
from typing import Iterable, Optional

use_match_typing: Incomplete

def typed_namedtuple(typename: str, field_names: list[str] | str | list[tuple[str, object]], *, rename: bool = ..., defaults: Optional[Iterable] = ..., module: Optional[str] = ...) -> object: ...
