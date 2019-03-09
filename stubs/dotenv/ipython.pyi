from IPython.core.magic import Magics  # type: ignore
from typing import Any

class IPythonDotEnv(Magics):
    def dotenv(self, line: Any) -> None: ...

def load_ipython_extension(ipython: Any) -> None: ...
