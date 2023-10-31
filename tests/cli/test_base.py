"""Basic CLI tests"""


import pytest
from pytest_mock import MockerFixture
from requests_mock import adapter
from requests_mock.mocker import Mocker as RequestsMocker
from typer.testing import CliRunner

from tests.conftest import FakeFs
from varfish_cli import exceptions
from varfish_cli.cli import app


def test_project_list_empty_config(
    runner: CliRunner,
    fake_fs_empty_config: FakeFs,
    requests_mock: RequestsMocker,
    mocker: MockerFixture,
):
    """Test that we fail if no server configuration is present."""
    mocker.patch("varfish_cli.config.open", fake_fs_empty_config.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_empty_config.os)

    m = requests_mock.register_uri(adapter.ANY, adapter.ANY, text="resp")
    with pytest.raises(exceptions.InvalidConfiguration):
        runner.invoke(app, ["--verbose", "projects", "project-list"])

    mocker.stopall()

    assert m.request_history == []
