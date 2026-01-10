import os
import sys
import textwrap
from typing import List
from unittest import mock
from zipfile import ZipFile

import pytest

if sys.platform != "win32":
    import sh


def walk_to_root(path: str):
    last_dir = None
    current_dir = path
    while last_dir != current_dir:
        yield current_dir
        (parent_dir, _) = os.path.split(current_dir)
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
            for dirname in walk_to_root(os.path.dirname(f.path)):
                if dirname not in dirs_init_py_added_to:
                    print(os.path.join(dirname, "__init__.py"))
                    zipfile.writestr(
                        data="", zinfo_or_arcname=os.path.join(dirname, "__init__.py")
                    )
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


@pytest.mark.skipif(sys.platform == "win32", reason="sh module doesn't support Windows")
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
    dotenv_path.write_bytes(b"a=b")
    code_path = tmp_path / "code.py"
    code_path.write_text(
        textwrap.dedent(
            f"""
        import os
        import sys

        sys.path.append("{zip_file_path}")

        import child1.child2.test

        print(os.environ['a'])
    """
        )
    )
    os.chdir(str(tmp_path))

    result = sh.Command(sys.executable)(code_path)

    assert result == "b\n"
