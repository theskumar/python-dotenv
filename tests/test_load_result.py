import io
import os
from unittest import mock

import pytest

from dotenv import dotenv_values, load_dotenv


@pytest.mark.parametrize("override", [False, True])
@pytest.mark.parametrize("source", ["file", "stream"])
@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize(
    "content", ["DOTENV_TEST_KEY", "# comment\nDOTENV_TEST_KEY\nOTHER_KEY\n"]
)
def test_load_dotenv_without_values_returns_false(
    tmp_path, override, source, existing, content
):
    environ = {"DOTENV_TEST_KEY": "existing"} if existing else {}
    with mock.patch.dict(os.environ, environ, clear=True):
        if source == "file":
            path = tmp_path / ".env"
            path.write_text(content)
            result = load_dotenv(path, override=override)
        else:
            result = load_dotenv(stream=io.StringIO(content), override=override)

        assert result is False
        assert os.environ == environ

    assert dotenv_values(stream=io.StringIO(content))["DOTENV_TEST_KEY"] is None


@pytest.mark.parametrize("override", [False, True])
@pytest.mark.parametrize(
    "content",
    [
        "DOTENV_TEST_KEY=",
        "BARE_KEY\nDOTENV_TEST_KEY=",
        "DOTENV_TEST_KEY=value\nBARE_KEY",
    ],
)
def test_load_dotenv_with_values_returns_true(override, content):
    with mock.patch.dict(os.environ, {}, clear=True):
        result = load_dotenv(stream=io.StringIO(content), override=override)

        assert result is True
        assert os.environ == {"DOTENV_TEST_KEY": "value" if "=value" in content else ""}
