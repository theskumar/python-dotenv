import pytest

from .fixtures import *  # noqa


@pytest.fixture
def dotenv_file(tmpdir):
    file_ = tmpdir.mkdir('dotenv_file').join('.env')
    file_.write('')
    return str(file_)
