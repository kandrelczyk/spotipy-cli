import pytest
from click.testing import CliRunner
from spotipy_cli import __main__ as main


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(main.cli)
    assert result.exit_code == 0
    assert not result.exception
