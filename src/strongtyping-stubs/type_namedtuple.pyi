from typing import Any

from strongtyping.docstring_typing import check_doc_str_type as check_doc_str_type
from strongtyping.strong_typing import match_typing as match_typing
from strongtyping.strong_typing_utils import check_type as check_type

use_match_typing: dict[bool, Any]

@match_typing
def typed_namedtuple(
    typename: str,
    field_names: list[str] | str | list[tuple[str, object]],
    *,
    rename: bool = False,
    defaults: list[Any] | tuple[Any, ...] | None = None,
    module: str | None = None,
) -> type: ...
