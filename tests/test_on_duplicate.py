import logging
import os
from unittest.mock import patch

import pytest

import dotenv
from dotenv.main import DotEnv


def _write_env(tmp_path, content):
    env_file = tmp_path / ".env"
    env_file.write_text(content)
    return env_file


class TestOnDuplicate:
    def test_warn_emits_warning(self, tmp_path):
        env_file = _write_env(tmp_path, "FOO=first\nBAR=ok\nFOO=second\n")
        with patch.object(logging.getLogger("dotenv.main"), "warning") as mock_warn:
            result = DotEnv(env_file, on_duplicate="warn").dict()
        assert mock_warn.called
        assert "Duplicate key" in mock_warn.call_args[0][0]
        assert result["FOO"] == "second"

    def test_raise_raises_valueerror(self, tmp_path):
        env_file = _write_env(tmp_path, "FOO=first\nFOO=second\n")
        with pytest.raises(ValueError, match="Duplicate key"):
            DotEnv(env_file, on_duplicate="raise").dict()

    def test_ignore_no_warning(self, tmp_path):
        env_file = _write_env(tmp_path, "FOO=first\nFOO=second\n")
        with patch.object(logging.getLogger("dotenv.main"), "warning") as mock_warn:
            result = DotEnv(env_file, on_duplicate="ignore").dict()
        assert not mock_warn.called
        assert result["FOO"] == "second"

    def test_invalid_option_raises(self, tmp_path):
        env_file = _write_env(tmp_path, "")
        with pytest.raises(ValueError, match="Invalid value for on_duplicate"):
            DotEnv(env_file, on_duplicate="bad-value")

    def test_load_dotenv_warn(self, tmp_path):
        env_file = _write_env(tmp_path, "MYKEY=first\nMYKEY=second\n")
        with patch.object(logging.getLogger("dotenv.main"), "warning") as mock_warn:
            dotenv.load_dotenv(env_file, override=True, on_duplicate="warn")
        assert mock_warn.called
        assert "Duplicate key" in mock_warn.call_args[0][0]
        del os.environ["MYKEY"]

    def test_load_dotenv_raise(self, tmp_path):
        env_file = _write_env(tmp_path, "MYKEY=first\nMYKEY=second\n")
        with pytest.raises(ValueError, match="Duplicate key"):
            dotenv.load_dotenv(env_file, on_duplicate="raise")

    def test_dotenv_values_warn(self, tmp_path):
        env_file = _write_env(tmp_path, "Z=1\nZ=2\n")
        with patch.object(logging.getLogger("dotenv.main"), "warning") as mock_warn:
            result = dotenv.dotenv_values(env_file, on_duplicate="warn")
        assert mock_warn.called
        assert result["Z"] == "2"

    def test_dotenv_values_raise(self, tmp_path):
        env_file = _write_env(tmp_path, "Z=1\nZ=2\n")
        with pytest.raises(ValueError, match="Duplicate key"):
            dotenv.dotenv_values(env_file, on_duplicate="raise")

    def test_no_duplicate_no_warning(self, tmp_path):
        env_file = _write_env(tmp_path, "A=1\nB=2\n")
        with patch.object(logging.getLogger("dotenv.main"), "warning") as mock_warn:
            result = dotenv.dotenv_values(env_file, on_duplicate="warn")
        assert not mock_warn.called
        assert result == {"A": "1", "B": "2"}
