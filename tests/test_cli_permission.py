"""Command-launch permission failures should be CLI diagnostics, not tracebacks."""

import os
import sys

import pytest

from dotenv.cli import run_command
from tests.test_lib import run_dotenv


@pytest.mark.parametrize("platform", ["linux", "win32"])
def test_permission_error_is_reported_on_both_launch_paths(
    monkeypatch, capsys, platform
):
    import dotenv.cli as module

    def denied(*args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(module.sys, "platform", platform)
    monkeypatch.setattr(module.os, "execvpe", denied)
    monkeypatch.setattr(module, "Popen", denied, raising=False)
    with pytest.raises(SystemExit) as caught:
        run_command(["no-execute"], {"PRIVATE_TOKEN": "must-not-appear"})
    assert caught.value.code == 1
    output = capsys.readouterr().err
    assert "Permission denied: no-execute" in output
    assert "must-not-appear" not in output


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX execute bits")
@pytest.mark.parametrize("target_kind", ["file", "directory"])
def test_run_nonexecutable_target_has_no_traceback(tmp_path, target_kind):
    (tmp_path / ".env").write_text("A=b\n")
    target = tmp_path / "not-executable"
    if target_kind == "file":
        target.write_text("#!/bin/sh\nexit 0\n")
        target.chmod(0o600)
    else:
        target.mkdir()
    result = run_dotenv(["run", os.fspath(target)], cwd=tmp_path)
    assert result.returncode == 1
    assert "Permission denied:" in result.stderr
    assert "Traceback" not in result.stderr
