"""Optional parser bridge for the backend-only distribution.

``fast-dotenv-rs-backend`` is deliberately separate from the upstream
``dotenv`` package.  Its only adapter contract is a ``parse_bindings``
function returning lossless records in the order
``(key, value, original_string, original_line, error)``.

The Python parser is the normal path.  It is selected only when the backend
package is absent (or when running on PyPy).  Once a backend is imported, an
exception or contract violation is raised instead of being hidden by a
fallback; this keeps native semantic mismatches observable.
"""

from importlib import import_module
from platform import python_implementation
from typing import Iterator, Optional, Tuple

BindingRecord = Tuple[Optional[str], Optional[str], str, int, bool]

_BACKEND_MODULE = "fast_dotenv_rs_backend"
_BACKEND_DISTRIBUTION = "fast-dotenv-rs-backend"


class NativeBackendContractError(RuntimeError):
    """The selected backend did not satisfy the parser adapter contract."""


def _normalize_record(record: object) -> BindingRecord:
    if not isinstance(record, tuple) or len(record) != 5:
        raise NativeBackendContractError(
            "native parse_bindings record must be a five-item tuple"
        )

    key, value, original, line, error = record
    if key is not None and not isinstance(key, str):
        raise NativeBackendContractError("native binding key must be str or None")
    if value is not None and not isinstance(value, str):
        raise NativeBackendContractError("native binding value must be str or None")
    if not isinstance(original, str) or type(line) is not int or line < 1:
        raise NativeBackendContractError(
            "native binding original must be str and line must be a positive int"
        )
    if type(error) is not bool:
        raise NativeBackendContractError("native binding error must be bool")

    return key, value, original, line, error


def parse_bindings(text: str) -> Optional[Iterator[BindingRecord]]:
    """Return validated native records, or ``None`` when no backend is present."""
    if python_implementation() == "PyPy":
        return None

    try:
        backend = import_module(_BACKEND_MODULE)
    except ModuleNotFoundError as error:
        if error.name == _BACKEND_MODULE:
            return None
        raise

    parser = getattr(backend, "parse_bindings", None)
    if not callable(parser):
        raise NativeBackendContractError(
            f"{_BACKEND_DISTRIBUTION} does not expose parse_bindings"
        )

    records = [_normalize_record(record) for record in parser(text)]
    return iter(records)
