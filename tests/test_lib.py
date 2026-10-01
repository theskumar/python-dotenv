import subprocess
from pathlib import Path
from typing import Sequence


def run_dotenv(
    args: Sequence[str],
    cwd: str | Path | None = None,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """
    Run the `dotenv` CLI in a subprocess with the given arguments.
    """

    process = subprocess.run(
        ["dotenv", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )

    return process


def check_process(
    process: subprocess.CompletedProcess,
    exit_code: int,
    stdout: str | None = None,
):
    """
    Check that the process completed with the expected exit code and output.

    This provides better error messages than directly checking the attributes.
    """

    assert process.returncode == exit_code, (
        f"Unexpected exit code {process.returncode} (expected {exit_code})\n"
        f"stdout:\n{process.stdout}\n"
        f"stderr:\n{process.stderr}"
    )

    if stdout is not None:
        assert process.stdout == stdout, (
            f"Unexpected output: {process.stdout.strip()!r} (expected {stdout!r})"
        )
