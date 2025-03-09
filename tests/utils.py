import os
import platform
import subprocess
from contextlib import contextmanager
from typing import Dict, Optional, Union, List

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    printenv_cmd = ["cmd", "/c", "echo", "%a%"]
else:
    printenv_cmd = ["printenv", "a"]


@contextmanager
def pushd(path):
    """Context manager for changing the current working directory temporarily."""
    prev_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_dir)


def run_command(
    cmd: Union[str, List[str]],
    env: Optional[Dict[str, str]] = None,
    capture_output: bool = True,
) -> str:
    """
    Run a shell command and return its output.

    Args:
        cmd: Command string or list of command args
        env: Environment variables to use
        capture_output: Whether to capture and return output

    Returns:
        Command output as string
    """
    if env is None:
        env = os.environ.copy()

    # Convert string command to list for subprocess if needed
    if isinstance(cmd, str):
        if IS_WINDOWS:
            # Windows needs shell=True for built-ins
            result = subprocess.run(
                cmd, env=env, shell=True, text=True, capture_output=capture_output
            )
        else:
            # For Unix, better to split the command
            result = subprocess.run(
                cmd.split(), env=env, text=True, capture_output=capture_output
            )
    else:
        # List of args (already split)
        result = subprocess.run(cmd, env=env, text=True, capture_output=capture_output)

    if result.returncode != 0:
        stderr = result.stderr if hasattr(result, "stderr") else ""
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, stderr
        )

    return result.stdout
