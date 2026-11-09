import io
import sys
from pathlib import Path
from types import ModuleType

import pytest

import dotenv
import dotenv._native as native
import dotenv.parser as parser_module
from dotenv.parser import Binding, Original, parse_stream

native_only = pytest.mark.skipif(
    sys.implementation.name == "pypy",
    reason="native backend contract tests require CPython",
)


def _python_bindings(text):
    return list(parse_stream(io.StringIO(text)))


def _mark_backend(backend):
    backend.BACKEND_CONTRACT = native._BACKEND_CONTRACT
    backend.BACKEND_CONTRACT_VERSION = native._BACKEND_CONTRACT_VERSION
    return backend


def test_missing_backend_falls_back_to_python_parser(monkeypatch):
    def missing_backend(module_name):
        raise ModuleNotFoundError(module_name, name=module_name)

    monkeypatch.setattr(native, "import_module", missing_backend)

    assert _python_bindings("a=b\n") == [
        Binding(
            key="a",
            value="b",
            original=Original(string="a=b\n", line=1),
            error=False,
        )
    ]


@native_only
def test_backend_exception_is_not_hidden_by_python_fallback(monkeypatch):
    class BrokenBackend:
        @staticmethod
        def parse_bindings(text):
            raise RuntimeError("backend semantic failure")

    monkeypatch.setattr(native, "import_module", lambda _: _mark_backend(BrokenBackend))

    with pytest.raises(RuntimeError, match="backend semantic failure"):
        _python_bindings("a=b\n")


@pytest.mark.parametrize(
    "records",
    [
        [("a", "b", "a=b", 1)],
        [("a", "b", "a=b", 1, "false")],
        [("a", "b", "a=b", 0, False)],
    ],
)
@native_only
def test_invalid_backend_records_are_hard_contract_errors(monkeypatch, records):
    class InvalidBackend:
        @staticmethod
        def parse_bindings(text):
            return records

    monkeypatch.setattr(
        native, "import_module", lambda _: _mark_backend(InvalidBackend)
    )

    with pytest.raises(native.NativeBackendContractError):
        _python_bindings("a=b\n")


@native_only
def test_backend_import_dependency_error_is_not_hidden(monkeypatch):
    def broken_import(module_name):
        raise ModuleNotFoundError("backend dependency missing", name="dependency")

    monkeypatch.setattr(native, "import_module", broken_import)

    with pytest.raises(ModuleNotFoundError, match="backend dependency missing"):
        _python_bindings("a=b\n")


def test_pypy_never_attempts_native_import(monkeypatch):
    monkeypatch.setattr(native, "python_implementation", lambda: "PyPy")
    monkeypatch.setattr(
        native,
        "import_module",
        lambda _: pytest.fail("PyPy must not import a native backend"),
    )

    assert _python_bindings("a=b\n") == [
        Binding(
            key="a",
            value="b",
            original=Original(string="a=b\n", line=1),
            error=False,
        )
    ]


@native_only
def test_backend_contract_markers_are_required(monkeypatch):
    class UnversionedBackend:
        @staticmethod
        def parse_bindings(text):
            return [("a", "b", "a=b\n", 1, False)]

    monkeypatch.setattr(native, "import_module", lambda _: UnversionedBackend)

    with pytest.raises(
        native.NativeBackendContractError, match="supported parser contract"
    ):
        _python_bindings("a=b\n")


@native_only
def test_backend_contract_marker_mismatch_is_not_hidden(monkeypatch):
    class WrongContractBackend:
        BACKEND_CONTRACT = "wrong.contract"
        BACKEND_CONTRACT_VERSION = 99

        @staticmethod
        def parse_bindings(text):
            return [("a", "b", "a=b\n", 1, False)]

    monkeypatch.setattr(native, "import_module", lambda _: WrongContractBackend)

    with pytest.raises(
        native.NativeBackendContractError, match="supported parser contract"
    ):
        _python_bindings("a=b\n")


@native_only
def test_valid_backend_records_are_adapted_at_parser_boundary(monkeypatch):
    calls = []

    class Backend:
        @staticmethod
        def parse_bindings(text):
            calls.append(text)
            return [("a", "b", "a=b\n", 1, False)]

    monkeypatch.setattr(native, "import_module", lambda _: _mark_backend(Backend))
    monkeypatch.setattr(
        parser_module,
        "parse_binding",
        lambda _: pytest.fail("native path must not duplicate Python parsing"),
    )

    result = list(parse_stream(io.StringIO("\ufeffa=b\n")))

    assert calls == ["a=b\n"]
    assert result == [
        Binding(
            key="a",
            value="b",
            original=Original(string="a=b\n", line=1),
            error=False,
        )
    ]
    assert type(result[0]) is Binding
    assert type(result[0].original) is Original


@native_only
def test_legacy_dotenv_core_is_not_used(monkeypatch):
    calls = []

    def missing_backend(module_name):
        calls.append(module_name)
        raise ModuleNotFoundError(module_name, name=module_name)

    monkeypatch.setattr(native, "import_module", missing_backend)
    assert _python_bindings("a=b\n")[0].value == "b"
    assert calls == ["fast_dotenv_rs_backend"]


@native_only
def test_extension_only_backend_can_coexist_with_upstream_package(monkeypatch):
    backend = ModuleType(native._BACKEND_MODULE)
    _mark_backend(backend)
    backend.__dict__["parse_bindings"] = lambda text: [("a", "b", "a=b", 1, False)]
    monkeypatch.setitem(sys.modules, native._BACKEND_MODULE, backend)

    result = list(parse_stream(io.StringIO("a=b")))

    assert Path(dotenv.__file__).name == "__init__.py"
    assert dotenv.__all__ == [
        "get_cli_string",
        "load_dotenv",
        "dotenv_values",
        "get_key",
        "set_key",
        "unset_key",
        "find_dotenv",
        "load_ipython_extension",
    ]
    assert result == [
        Binding(
            key="a",
            value="b",
            original=Original(string="a=b", line=1),
            error=False,
        )
    ]
