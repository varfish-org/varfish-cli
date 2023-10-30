import json
import typing

import pytest
from pytest_mock import MockerFixture
from pytest_snapshot.plugin import Snapshot
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
    mocker.patch("varfish_cli.config.open", fake_fs_empty_config.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_empty_config.os)

    m = requests_mock.register_uri(adapter.ANY, adapter.ANY, text="resp")
    with pytest.raises(exceptions.InvalidConfiguration):
        runner.invoke(app, ["--verbose", "projects", "project-list"])

    mocker.stopall()

    assert m.request_history == []


@pytest.fixture
def project_list_result_empty() -> typing.List[typing.Any]:
    return []


def test_project_list_configured_empty(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    project_list_result_empty,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/project/api/list",
        json=project_list_result_empty,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(app, ["--verbose", "projects", "project-list", "--output-format=json"])

    mocker.stopall()

    assert result.exit_code == 0
    assert result.output == "[]\n"


@pytest.fixture
def project_list_result_two_elements() -> typing.List[typing.Any]:
    with open("tests/cli/data/projects_project-list.len-2.json", "rt") as inputf:
        return json.load(inputf)


def test_project_list_configured_two_elements(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    project_list_result_two_elements,
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/project/api/list",
        json=project_list_result_two_elements,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(app, ["--verbose", "projects", "project-list", "--output-format=json"])

    mocker.stopall()

    assert result.exit_code == 0
    snapshot.assert_match(result.output, "result_output")
