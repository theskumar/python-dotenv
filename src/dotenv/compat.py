import sys
from typing import Text

if sys.version_info >= (3, 0):
    from io import StringIO  # noqa
else:
    from StringIO import StringIO  # noqa

PY2 = sys.version_info[0] == 2  # type: bool


def to_text(string):
    # type: (str) -> Text
    """
    Make a string Unicode if it isn't already.

    This is useful for defining raw unicode strings because `ur"foo"` isn't valid in
    Python 3.
    """
    if PY2:
        return string.decode("utf-8")
    else:
        return string
