"""Test CLI for projects API."""

import json
import typing
import uuid

import pytest
from pytest_mock import MockerFixture
from requests_mock.mocker import Mocker as RequestsMocker
from syrupy import SnapshotAssertion
from typer.testing import CliRunner

from tests.conftest import FakeFs
from varfish_cli.cli import app


@pytest.fixture
def project_list_result_empty() -> typing.List[typing.Any]:
    return []


def test_project_list_empty(
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

    assert result.exit_code == 0, result.output
    assert result.output == "[]\n"


@pytest.fixture
def project_list_result_two_elements() -> typing.List[typing.Any]:
    with open("tests/cli/data/projects_project-list.len-2.json", "rt") as inputf:
        return json.load(inputf)


def test_project_list_two_elements(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    project_list_result_two_elements,
    snapshot: SnapshotAssertion,
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

    assert result.exit_code == 0, result.output
    assert result.output == snapshot


@pytest.fixture
def project_retrieve_result() -> typing.List[typing.Any]:
    with open("tests/cli/data/projects_project-list.len-2.json", "rt") as inputf:
        return json.load(inputf)[0]


def test_project_retrieve(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    project_retrieve_result,
    snapshot: SnapshotAssertion,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/project/api/retrieve/{project_uuid}",
        json=project_retrieve_result,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(app, ["--verbose", "projects", "project-retrieve", project_uuid])

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == snapshot
