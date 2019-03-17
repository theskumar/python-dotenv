from typing import Text, Type
import sys
if sys.version_info >= (3, 0):
    from io import StringIO  # noqa
else:
    from StringIO import StringIO  # noqa

PY2 = sys.version_info[0] == 2  # type: bool
WIN = sys.platform.startswith('win')  # type: bool
text_type = Text  # type: Type[Text]
