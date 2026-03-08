import io
import logging
import os
import pathlib
import stat
import sys
import tempfile
from collections import OrderedDict
from contextlib import contextmanager
from typing import IO, Dict, Iterable, Iterator, Mapping, Optional, Tuple, Union

from .parser import Binding, parse_stream
from .variables import parse_variables

# A type alias for a string path to be used for the paths in this file.
# These paths may flow to `open()` and `os.replace()`.
StrPath = Union[str, "os.PathLike[str]"]

logger = logging.getLogger(__name__)


def _load_dotenv_disabled() -> bool:
    """Return ``True`` if the ``PYTHON_DOTENV_DISABLED`` env var is set to a truthy value."""
    if "PYTHON_DOTENV_DISABLED" not in os.environ:
        return False
    value = os.environ["PYTHON_DOTENV_DISABLED"].casefold()
    return value in {"1", "true", "t", "yes", "y"}


def with_warn_for_invalid_lines(mappings: Iterator[Binding]) -> Iterator[Binding]:
    """Yield each binding, logging a warning for any that failed to parse."""
    for mapping in mappings:
        if mapping.error:
            logger.warning(
                "python-dotenv could not parse statement starting at line %s",
                mapping.original.line,
            )
        yield mapping


class DotEnv:
    """Parse a ``.env`` file and expose its key-value pairs.

    Provide the content either as a filesystem path via *dotenv_path* or as an
    already-opened text stream via *stream*.  Variable interpolation
    (``${VAR}`` syntax) is performed by default and can be disabled with
    *interpolate*.

    Attributes:
        dotenv_path: Path to the ``.env`` file, or ``None`` when using a stream.
        encoding: Encoding used to open the file.
        interpolate: Whether ``${VAR}`` references in values are resolved.
        override: Whether dotenv values take precedence over existing
            environment variables during interpolation.
    """

    def __init__(
        self,
        dotenv_path: Optional[StrPath],
        stream: Optional[IO[str]] = None,
        verbose: bool = False,
        encoding: Optional[str] = None,
        interpolate: bool = True,
        override: bool = True,
    ) -> None:
        self.dotenv_path: Optional[StrPath] = dotenv_path
        self.stream: Optional[IO[str]] = stream
        self._dict: Optional[Dict[str, Optional[str]]] = None
        self.verbose: bool = verbose
        self.encoding: Optional[str] = encoding
        self.interpolate: bool = interpolate
        self.override: bool = override

    @contextmanager
    def _get_stream(self) -> Iterator[IO[str]]:
        if self.dotenv_path and _is_file_or_fifo(self.dotenv_path):
            with open(self.dotenv_path, encoding=self.encoding) as stream:
                yield stream
        elif self.stream is not None:
            yield self.stream
        else:
            if self.verbose:
                logger.info(
                    "python-dotenv could not find configuration file %s.",
                    self.dotenv_path or ".env",
                )
            yield io.StringIO("")

    def dict(self) -> Dict[str, Optional[str]]:
        """Return the parsed .env content as an ordered dictionary.

        Results are cached after the first call. If interpolation is enabled,
        variable references (e.g. ``${VAR}``) within values are resolved
        against previously parsed dotenv values and the system environment.

        Returns:
            An ordered dict mapping variable names to their values.
            Keys declared without a value will have ``None`` as their value.
        """
        if self._dict:
            return self._dict

        raw_values = self.parse()

        if self.interpolate:
            self._dict = OrderedDict(
                resolve_variables(raw_values, override=self.override)
            )
        else:
            self._dict = OrderedDict(raw_values)

        return self._dict

    def parse(self) -> Iterator[Tuple[str, Optional[str]]]:
        """Yield ``(key, value)`` pairs parsed from the ``.env`` source."""
        with self._get_stream() as stream:
            for mapping in with_warn_for_invalid_lines(parse_stream(stream)):
                if mapping.key is not None:
                    yield mapping.key, mapping.value

    def set_as_environment_variables(self) -> bool:
        """Set all parsed key-value pairs as environment variables.

        Returns:
            ``True`` if at least one variable was present, ``False`` otherwise.
        """
        if not self.dict():
            return False

        for k, v in self.dict().items():
            if k in os.environ and not self.override:
                continue
            if v is not None:
                os.environ[k] = v

        return True

    def get(self, key: str) -> Optional[str]:
        """Return the value for *key*, or ``None`` if it is not present."""
        data = self.dict()

        if key in data:
            return data[key]

        if self.verbose:
            logger.warning("Key %s not found in %s.", key, self.dotenv_path)

        return None


def get_key(
    dotenv_path: StrPath,
    key_to_get: str,
    encoding: Optional[str] = "utf-8",
) -> Optional[str]:
    """Return the value of *key_to_get* from the ``.env`` file at *dotenv_path*.

    Return ``None`` if the key is absent or declared without a value.
    """
    return DotEnv(dotenv_path, verbose=True, encoding=encoding).get(key_to_get)


@contextmanager
def rewrite(
    path: StrPath,
    encoding: Optional[str],
    follow_symlinks: bool = False,
) -> Iterator[Tuple[IO[str], IO[str]]]:
    """Context manager for atomically rewriting a file.

    Yields a ``(source, dest)`` pair of text streams. ``source`` is the
    existing file opened for reading (or an empty ``StringIO`` if the file
    doesn't exist yet). ``dest`` is a temporary file in the same directory
    opened for writing. The caller should read from ``source`` and write the
    desired new content to ``dest``.

    On a clean exit the temporary file is moved into place via
    ``os.replace()``, preserving the original file's permission bits. If an
    exception occurs, the temporary file is removed and the original is left
    untouched.

    Parameters:
        path: Path to the file to rewrite (created if it doesn't exist).
        encoding: Encoding used to open both the source and destination files.
        follow_symlinks: If ``True``, resolve symlinks so the real file is
            rewritten rather than replacing the symlink itself.
    """
    if follow_symlinks:
        path = os.path.realpath(path)

    try:
        source: IO[str] = open(path, encoding=encoding)
        try:
            path_stat = os.lstat(path)
            original_mode: Optional[int] = (
                stat.S_IMODE(path_stat.st_mode)
                if stat.S_ISREG(path_stat.st_mode)
                else None
            )
        except BaseException:
            source.close()
            raise
    except FileNotFoundError:
        source = io.StringIO("")
        original_mode = None

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding=encoding,
        delete=False,
        prefix=".tmp_",
        dir=os.path.dirname(os.path.abspath(path)),
    ) as dest:
        dest_path = pathlib.Path(dest.name)
        error = None

        try:
            with source:
                yield (source, dest)
        except BaseException as err:
            error = err

    if error is None:
        try:
            if original_mode is not None:
                os.chmod(dest_path, original_mode)

            os.replace(dest_path, path)
        except BaseException:
            dest_path.unlink(missing_ok=True)
            raise
    else:
        dest_path.unlink(missing_ok=True)
        raise error from None


def set_key(
    dotenv_path: StrPath,
    key_to_set: str,
    value_to_set: str,
    quote_mode: str = "always",
    export: bool = False,
    encoding: Optional[str] = "utf-8",
    follow_symlinks: bool = False,
) -> Tuple[Optional[bool], str, str]:
    """Add or update a key-value pair in the ``.env`` file at *dotenv_path*.

    Create the file if it does not already exist.  Symlinks are **not**
    followed by default to avoid writing to an untrusted target; set
    *follow_symlinks* to ``True`` to override this.

    Returns:
        A ``(True, key, value)`` tuple on success.

    Raises:
        ValueError: If *quote_mode* is not one of ``"always"``,
            ``"auto"``, or ``"never"``.
    """
    if quote_mode not in ("always", "auto", "never"):
        raise ValueError(f"Unknown quote_mode: {quote_mode}")

    quote = quote_mode == "always" or (
        quote_mode == "auto" and not value_to_set.isalnum()
    )

    if quote:
        value_out = "'{}'".format(value_to_set.replace("'", "\\'"))
    else:
        value_out = value_to_set
    if export:
        line_out = f"export {key_to_set}={value_out}\n"
    else:
        line_out = f"{key_to_set}={value_out}\n"

    with rewrite(dotenv_path, encoding=encoding, follow_symlinks=follow_symlinks) as (
        source,
        dest,
    ):
        replaced = False
        missing_newline = False
        for mapping in with_warn_for_invalid_lines(parse_stream(source)):
            if mapping.key == key_to_set:
                dest.write(line_out)
                replaced = True
            else:
                dest.write(mapping.original.string)
                missing_newline = not mapping.original.string.endswith("\n")
        if not replaced:
            if missing_newline:
                dest.write("\n")
            dest.write(line_out)

    return True, key_to_set, value_to_set


def unset_key(
    dotenv_path: StrPath,
    key_to_unset: str,
    quote_mode: str = "always",
    encoding: Optional[str] = "utf-8",
    follow_symlinks: bool = False,
) -> Tuple[Optional[bool], str]:
    """Remove *key_to_unset* from the ``.env`` file at *dotenv_path*.

    Return ``(None, key)`` and log a warning if the file does not exist or the
    key is not found.  Symlinks are **not** followed by default; set
    *follow_symlinks* to ``True`` to override this.

    Returns:
        ``(True, key)`` on success, ``(None, key)`` on failure.
    """
    if not os.path.exists(dotenv_path):
        logger.warning("Can't delete from %s - it doesn't exist.", dotenv_path)
        return None, key_to_unset

    removed = False
    with rewrite(dotenv_path, encoding=encoding, follow_symlinks=follow_symlinks) as (
        source,
        dest,
    ):
        for mapping in with_warn_for_invalid_lines(parse_stream(source)):
            if mapping.key == key_to_unset:
                removed = True
            else:
                dest.write(mapping.original.string)

    if not removed:
        logger.warning(
            "Key %s not removed from %s - key doesn't exist.", key_to_unset, dotenv_path
        )
        return None, key_to_unset

    return removed, key_to_unset


def resolve_variables(
    values: Iterable[Tuple[str, Optional[str]]],
    override: bool,
) -> Mapping[str, Optional[str]]:
    """Resolve variable interpolations in a sequence of key-value pairs.

    Replace variable references (e.g. ``${VAR}`` or ``$VAR``) within values by
    looking them up in the already-resolved dotenv values and the system
    environment. The *override* flag controls precedence: when ``True``, dotenv
    values take priority over existing environment variables; when ``False``,
    existing environment variables take priority over dotenv values.

    Parameters:
        values: An iterable of ``(key, value)`` pairs as produced by
            :meth:`DotEnv.parse`.  Values may be ``None`` for keys that were
            declared without an assignment.
        override: If ``True``, previously parsed dotenv values override system
            environment variables during interpolation.  If ``False``, system
            environment variables take precedence.

    Returns:
        An ordered mapping of resolved key-value pairs, preserving the
        original iteration order.
    """
    new_values: Dict[str, Optional[str]] = {}

    for name, value in values:
        if value is None:
            result = None
        else:
            atoms = parse_variables(value)
            env: Dict[str, Optional[str]] = {}
            if override:
                env.update(os.environ)
                env.update(new_values)
            else:
                env.update(new_values)
                env.update(os.environ)
            result = "".join(atom.resolve(env) for atom in atoms)

        new_values[name] = result

    return new_values


def _walk_to_root(path: str) -> Iterator[str]:
    """Yield directories starting from *path* up to the filesystem root."""
    if not os.path.exists(path):
        raise IOError("Starting path not found")

    if os.path.isfile(path):
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    while last_dir != current_dir:
        yield current_dir
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir


def find_dotenv(
    filename: str = ".env",
    raise_error_if_not_found: bool = False,
    usecwd: bool = False,
) -> str:
    """Search for a ``.env`` file by walking up from the caller's directory.

    Return the absolute path if found, or an empty string otherwise.
    """

    def _is_interactive():
        """Decide whether this is running in a REPL or IPython notebook"""
        if hasattr(sys, "ps1") or hasattr(sys, "ps2"):
            return True
        try:
            main = __import__("__main__", None, None, fromlist=["__file__"])
        except ModuleNotFoundError:
            return False
        return not hasattr(main, "__file__")

    def _is_debugger():
        return sys.gettrace() is not None

    if usecwd or _is_interactive() or _is_debugger() or getattr(sys, "frozen", False):
        # Should work without __file__, e.g. in REPL or IPython notebook.
        path = os.getcwd()
    else:
        # will work for .py files
        frame = sys._getframe()
        current_file = __file__

        while frame.f_code.co_filename == current_file or not os.path.exists(
            frame.f_code.co_filename
        ):
            assert frame.f_back is not None
            frame = frame.f_back
        frame_filename = frame.f_code.co_filename
        path = os.path.dirname(os.path.abspath(frame_filename))

    for dirname in _walk_to_root(path):
        check_path = os.path.join(dirname, filename)
        if _is_file_or_fifo(check_path):
            return check_path

    if raise_error_if_not_found:
        raise IOError("File not found")

    return ""


def load_dotenv(
    dotenv_path: Optional[StrPath] = None,
    stream: Optional[IO[str]] = None,
    verbose: bool = False,
    override: bool = False,
    interpolate: bool = True,
    encoding: Optional[str] = "utf-8",
) -> bool:
    """Parse a .env file and then load all the variables found as environment variables.

    Parameters:
        dotenv_path: Absolute or relative path to .env file.
        stream: Text stream (such as `io.StringIO`) with .env content, used if
            `dotenv_path` is `None`.
        verbose: Whether to output a warning the .env file is missing.
        override: Whether to override the system environment variables with the variables
            from the `.env` file.
        encoding: Encoding to be used to read the file.

    Returns:
        Bool: True if at least one environment variable is set else False

    If both `dotenv_path` and `stream` are `None`, `find_dotenv()` is used to find the
    .env file with it's default parameters. If you need to change the default parameters
    of `find_dotenv()`, you can explicitly call `find_dotenv()` and pass the result
    to this function as `dotenv_path`.

    If the environment variable `PYTHON_DOTENV_DISABLED` is set to a truthy value,
    .env loading is disabled.
    """
    if _load_dotenv_disabled():
        logger.debug(
            "python-dotenv: .env loading disabled by PYTHON_DOTENV_DISABLED environment variable"
        )
        return False

    if dotenv_path is None and stream is None:
        dotenv_path = find_dotenv()

    dotenv = DotEnv(
        dotenv_path=dotenv_path,
        stream=stream,
        verbose=verbose,
        interpolate=interpolate,
        override=override,
        encoding=encoding,
    )
    return dotenv.set_as_environment_variables()


def dotenv_values(
    dotenv_path: Optional[StrPath] = None,
    stream: Optional[IO[str]] = None,
    verbose: bool = False,
    interpolate: bool = True,
    encoding: Optional[str] = "utf-8",
) -> Dict[str, Optional[str]]:
    """Parse a ``.env`` file and return its content as a dict.

    Keys declared without a value (e.g. bare ``FOO``) will have ``None`` as
    their dict value.

    Args:
        dotenv_path: Absolute or relative path to the ``.env`` file.
        stream: Text stream with ``.env`` content, used if *dotenv_path* is
            ``None``.
        verbose: Whether to log a warning when the ``.env`` file is missing.
        interpolate: Whether to resolve ``${VAR}`` references in values.
        encoding: Encoding used to read the file.

    If both *dotenv_path* and *stream* are ``None``, :func:`find_dotenv` is
    used to locate the ``.env`` file.
    """
    if dotenv_path is None and stream is None:
        dotenv_path = find_dotenv()

    return DotEnv(
        dotenv_path=dotenv_path,
        stream=stream,
        verbose=verbose,
        interpolate=interpolate,
        override=True,
        encoding=encoding,
    ).dict()


def _is_file_or_fifo(path: StrPath) -> bool:
    """Return ``True`` if *path* exists and is a regular file or a FIFO."""
    if os.path.isfile(path):
        return True

    try:
        st = os.stat(path)
    except (FileNotFoundError, OSError):
        return False

    return stat.S_ISFIFO(st.st_mode)
