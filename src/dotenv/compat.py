def is_type_checking():
    # type: () -> bool
    try:
        from typing import TYPE_CHECKING
    except ImportError:
        return False
    return TYPE_CHECKING


IS_TYPE_CHECKING = is_type_checking()
