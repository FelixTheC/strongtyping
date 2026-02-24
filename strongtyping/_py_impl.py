from typing import Any


def checking_typing_dict(arg: Any, possible_types: tuple, *args, **kwargs):
    if not isinstance(arg, dict):
        return False
    if isinstance(arg, dict) and not possible_types:
        return True
    try:
        key, val = possible_types
    except (ValueError, TypeError):
        return isinstance(arg, dict)
    else:
        from strongtyping.strong_typing_utils import check_type

        try:
            result_key = all(check_type(a, key) for a in arg.keys())
        except AttributeError:
            result_key = all(isinstance(k, key) for k in arg.keys())
        try:
            result_val = all(check_type(a, val) for a in arg.values())
        except AttributeError:
            result_val = all(isinstance(v, val) for v in arg.values())
        return result_key and result_val


def checking_typing_list(arg: Any, possible_types: tuple, *args, **kwargs):
    if not isinstance(arg, list):
        return False
    if isinstance(arg, list) and not possible_types:
        return True
    from strongtyping.strong_typing_utils import check_type

    possible_type = possible_types[0]
    return all(check_type(argument, possible_type, **kwargs) for argument in arg)


def checking_typing_set(arg: Any, possible_types: tuple, *args, **kwargs):
    if not possible_types:
        return isinstance(arg, set)
    from strongtyping.strong_typing_utils import check_type

    possible_type = possible_types[0]
    return isinstance(arg, set) and all(
        check_type(argument, possible_type, **kwargs) for argument in arg
    )


def checking_typing_tuple(arg: Any, possible_types: tuple, *args, **kwargs):
    if not possible_types:
        return isinstance(arg, tuple)
    from strongtyping.strong_typing_utils import check_type, checking_ellipsis

    if Ellipsis in possible_types and isinstance(arg, tuple):
        if not arg:
            return True
        return checking_ellipsis(arg, possible_types, **kwargs)
    if not isinstance(arg, tuple) or not (len(arg) == len(possible_types)):
        return False
    return all(check_type(argument, typ, **kwargs) for argument, typ in zip(arg, possible_types))
