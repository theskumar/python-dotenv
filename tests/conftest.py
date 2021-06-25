import pytest
from click.testing import CliRunner


@pytest.fixture
def cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture
def dotenv_file(tmp_path):
    file_ = tmp_path / '.env'
    file_.write_bytes(b'')
    yield str(file_)
