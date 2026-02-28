import os
import posixpath
import subprocess
import sys
import textwrap
from typing import List
from unittest import mock
from zipfile import ZipFile


def walk_to_root(path: str):
    last_dir = None
    current_dir = path
    while last_dir != current_dir:
        yield current_dir
        parent_dir = posixpath.dirname(current_dir)
        last_dir, current_dir = current_dir, parent_dir


class FileToAdd:
    def __init__(self, content: str, path: str):
        self.content = content
        self.path = path


def setup_zipfile(path, files: List[FileToAdd]):
    zip_file_path = path / "test.zip"
    dirs_init_py_added_to = set()
    with ZipFile(zip_file_path, "w") as zipfile:
        for f in files:
            zipfile.writestr(data=f.content, zinfo_or_arcname=f.path)
            for dirname in walk_to_root(posixpath.dirname(f.path)):
                if dirname not in dirs_init_py_added_to:
                    init_path = posixpath.join(dirname, "__init__.py")
                    print(f"setup_zipfile: {init_path}")
                    zipfile.writestr(data="", zinfo_or_arcname=init_path)
                    dirs_init_py_added_to.add(dirname)
    return zip_file_path


@mock.patch.object(sys, "path", list(sys.path))
def test_load_dotenv_gracefully_handles_zip_imports_when_no_env_file(tmp_path):
    zip_file_path = setup_zipfile(
        tmp_path,
        [
            FileToAdd(
                content=textwrap.dedent(
                    """
            from dotenv import load_dotenv

            load_dotenv()
        """
                ),
                path="child1/child2/test.py",
            ),
        ],
    )

    # Should run without an error
    sys.path.append(str(zip_file_path))
    import child1.child2.test  # noqa


def test_load_dotenv_outside_zip_file_when_called_in_zipfile(tmp_path):
    zip_file_path = setup_zipfile(
        tmp_path,
        [
            FileToAdd(
                content=textwrap.dedent(
                    """
            from dotenv import load_dotenv

            load_dotenv()
        """
                ),
                path="child1/child2/test.py",
            ),
        ],
    )
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_bytes(b"A=x")
    code_path = tmp_path / "code.py"
    code_path.write_text(
        textwrap.dedent(
            f"""
            import os
            import sys

            sys.path.append({str(zip_file_path)!r})

            import child1.child2.test

            print(os.environ['A'])
            """
        )
    )

    result = subprocess.run(
        [sys.executable, str(code_path)],
        capture_output=True,
        check=True,
        cwd=tmp_path,
        text=True,
        env={
            k: v for k, v in os.environ.items() if k.upper() != "A"
        },  # env without 'A'
    )

    assert result.stdout == "x\n"
