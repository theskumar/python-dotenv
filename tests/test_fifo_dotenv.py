import os
import pathlib
import sys
import threading

import pytest

from dotenv import load_dotenv
from tests.test_lib import check_process, run_dotenv

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="FIFOs are Unix-only")


def test_load_dotenv_from_fifo(tmp_path: pathlib.Path, monkeypatch):
    fifo = tmp_path / ".env"
    os.mkfifo(fifo)  # create named pipe

    def writer():
        with open(fifo, "w", encoding="utf-8") as w:
            w.write("MY_PASSWORD=pipe-secret\n")

    t = threading.Thread(target=writer)
    t.start()

    # Ensure env is clean
    monkeypatch.delenv("MY_PASSWORD", raising=False)

    ok = load_dotenv(dotenv_path=str(fifo), override=True)
    t.join(timeout=2)

    assert ok is True
    assert os.getenv("MY_PASSWORD") == "pipe-secret"


def test_cli_run_from_fifo(tmp_path: pathlib.Path):
    fifo = tmp_path / ".env"
    os.mkfifo(fifo)

    def writer():
        with open(fifo, "w", encoding="utf-8") as w:
            w.write("MY_PASSWORD=pipe-secret\n")

    # A daemon thread, so that a reader which never opens the FIFO can't hang
    # the test session.
    t = threading.Thread(target=writer, daemon=True)
    t.start()

    result = run_dotenv(["run", "printenv", "MY_PASSWORD"], cwd=tmp_path)
    t.join(timeout=2)

    check_process(result, exit_code=0, stdout="pipe-secret\n")
