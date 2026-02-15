import os
import pathlib
import sys
import threading

import pytest

from dotenv import load_dotenv
from dotenv.main import _wait_for_file_content

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


def test_wait_for_file_content_with_regular_file(tmp_path: pathlib.Path):
    """Test that _wait_for_file_content handles regular files correctly."""
    regular_file = tmp_path / ".env"
    regular_file.write_text("KEY=value\n", encoding="utf-8")

    stream = _wait_for_file_content(str(regular_file), encoding="utf-8")
    content = stream.read()

    assert content == "KEY=value\n"
    stream.close()


def test_wait_for_file_content_with_fifo(tmp_path: pathlib.Path):
    """Test that _wait_for_file_content handles FIFOs correctly."""
    fifo = tmp_path / ".env"
    os.mkfifo(fifo)

    def writer():
        with open(fifo, "w", encoding="utf-8") as w:
            w.write("FIFO_KEY=fifo-value\n")

    t = threading.Thread(target=writer)
    t.start()

    stream = _wait_for_file_content(str(fifo), encoding="utf-8")
    content = stream.read()

    t.join(timeout=2)

    assert content == "FIFO_KEY=fifo-value\n"
