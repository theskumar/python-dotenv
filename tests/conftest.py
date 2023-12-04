import pytest
from click.testing import CliRunner


@pytest.fixture
def cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture
def dotenv_path(tmp_path):
    path = tmp_path / '.env'
    path.write_bytes(b'')
    yield path
