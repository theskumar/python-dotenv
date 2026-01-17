import os
from unittest import mock

import dotenv


@mock.patch.dict(os.environ, {}, clear=True)
def test_load_dotenv_multiline(tmp_path):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        """
BAZ1=baz
baz
baz
"""
    )
    dotenv.load_dotenv(dotenv_path)

    assert os.environ["BAZ1"] == "baz\nbaz\nbaz"
