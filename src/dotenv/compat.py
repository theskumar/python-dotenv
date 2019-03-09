from typing import Type, Text
import sys
try:
    from StringIO import StringIO  # type: ignore # noqa
except ImportError:
    from io import StringIO  # noqa

PY2: bool = sys.version_info[0] == 2
WIN: bool = sys.platform.startswith('win')
text_type: Type[Text] = unicode if PY2 else str  # type: ignore # noqa
