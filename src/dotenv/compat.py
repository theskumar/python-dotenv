from typing import Text, Type, TYPE_CHECKING
import sys
if sys.version_info >= (3, 0):
    from io import StringIO  # noqa
else:
    from StringIO import StringIO  # noqa

PY2 = sys.version_info[0] == 2  # type: bool
WIN = sys.platform.startswith('win')  # type: bool
if TYPE_CHECKING:
    text_type = Text  # type: Type[Text]
else:
    text_type = unicode if PY2 else str
