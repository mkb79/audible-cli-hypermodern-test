"""Test cases for the cli module."""
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner

from audible_cli import cli


if TYPE_CHECKING:
    import pathlib


@pytest.fixture()
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_cli_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0


def test_quickstart_succeeds(runner: CliRunner, tmp_path: "pathlib.Path", mocker) -> None:
    """It exits with a status code of zero."""
    mocker.patch("audible_cli.cmds.cmd_quickstart.build_auth_file")
    env = {
        "AUDIBLE_CONFIG_DIR": str(tmp_path.resolve())
    }
    input_ = "\n".join(
        [
            "\r",  # use default for the name of the primary profile
            "de",  # country code for profile
            "\r",  # use default for the name of the auth file
            "y\r",  # encrypt auth file
            "strongpassword\r",  # set password
            "strongpassword\r",  # confirm password
            "y\r",  # use external login
            "\r",  # use Amazon account instead of pre-Amazon
            "y\r",  # continue with settings
        ]
    )
    result = runner.invoke(cli.quickstart, input=input_, env=env)
    assert (tmp_path / "config.toml").exists()
    assert result.exit_code == 0
