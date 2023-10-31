"""Test CLI for importer API."""

import json
import typing
import uuid

import pytest
from pytest_mock import MockerFixture
from pytest_snapshot.plugin import Snapshot
from requests_mock.mocker import Mocker as RequestsMocker
from typer.testing import CliRunner

from tests.conftest import FakeFs
from varfish_cli.cli import app


@pytest.fixture
def caseimportinfo_list_result_empty() -> typing.List[typing.Any]:
    return []


def test_varannoset_list_empty(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    caseimportinfo_list_result_empty: typing.List[typing.Any],
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/importer/api/case-import-info/{project_uuid}/",
        json=caseimportinfo_list_result_empty,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(app, ["--verbose", "importer", "caseimportinfo-list", project_uuid])

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == "Case Import Info List\n=====================\n\nNo records found.\n"


@pytest.fixture
def caseimportinfo_list_result_two_elements() -> typing.List[typing.Any]:
    with open("tests/cli/data/caseimportinfo-list.len-2.json", "rt") as inputf:
        return json.load(inputf)


def test_varannoset_list_one_element(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    caseimportinfo_list_result_two_elements: typing.List[typing.Any],
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/importer/api/case-import-info/{project_uuid}/",
        json=caseimportinfo_list_result_two_elements,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(app, ["--verbose", "importer", "caseimportinfo-list", project_uuid])

    mocker.stopall()

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")
