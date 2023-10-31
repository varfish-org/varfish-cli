"""Test CLI for cases API."""

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
def case_list_result_empty() -> typing.List[typing.Any]:
    return {"count": 1, "next": None, "previous": None, "results": []}


def test_case_list_empty(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    case_list_result_empty,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/cases/api/case/list/{project_uuid}/",
        json=case_list_result_empty,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app, ["--verbose", "cases", "case-list", "--output-format=json", project_uuid]
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == "[]\n"


@pytest.fixture
def case_list_result_one_elements() -> typing.List[typing.Any]:
    with open("tests/cli/data/cases_case-list.len-1.json", "rt") as inputf:
        return json.load(inputf)


def test_case_list_one_element(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    case_list_result_one_elements,
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = case_list_result_one_elements["results"][0]["project"]
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/cases/api/case/list/{project_uuid}/",
        json=case_list_result_one_elements,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(app, ["--verbose", "cases", "case-list", project_uuid])

    mocker.stopall()

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")


def test_case_retrieve(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    case_list_result_one_elements,
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_json = case_list_result_one_elements["results"][0]
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/variants/api/case/retrieve/{obj_json['sodar_uuid']}",
        json=obj_json,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(app, ["--verbose", "cases", "case-retrieve", obj_json["sodar_uuid"]])

    mocker.stopall()

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")
