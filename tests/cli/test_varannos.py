"""Test CLI for varannos API."""

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
def varannoset_list_result_empty() -> typing.List[typing.Any]:
    return []


def test_varannoset_list_empty(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_empty,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/varannos/api/varannoset/list-create/{project_uuid}",
        json=varannoset_list_result_empty,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app, ["--verbose", "varannos", "varannoset-list", "--output-format=json", project_uuid]
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == "[]\n"


@pytest.fixture
def varannoset_list_result_one_elements() -> typing.List[typing.Any]:
    with open("tests/cli/data/varannos_varannoset-list.len-1.json", "rt") as inputf:
        return json.load(inputf)


def test_varannoset_list_one_element(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/varannos/api/varannoset/list-create/{project_uuid}",
        json=varannoset_list_result_one_elements,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app, ["--verbose", "varannos", "varannoset-list", "--output-format=json", project_uuid]
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")


def test_varannoset_retrieve(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_json = varannoset_list_result_one_elements[0]
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/varannos/api/varannoset/retrieve-update-destroy/{obj_json['sodar_uuid']}",
        json=obj_json,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app, ["--verbose", "varannos", "varannoset-retrieve", obj_json["sodar_uuid"]]
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")


def test_varannoset_update(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_json = varannoset_list_result_one_elements[0]
    host, token = fake_conn
    m = requests_mock.patch(
        f"{host}/varannos/api/varannoset/retrieve-update-destroy/{obj_json['sodar_uuid']}",
        json=obj_json,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app,
        [
            "--verbose",
            "varannos",
            "varannoset-update",
            obj_json["sodar_uuid"],
            json.dumps(obj_json),
        ],
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")


def test_varannoset_destroy(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_uuid = varannoset_list_result_one_elements[0]["sodar_uuid"]
    host, token = fake_conn
    m = requests_mock.delete(
        f"{host}/varannos/api/varannoset/retrieve-update-destroy/{obj_uuid}",
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app,
        ["--verbose", "varannos", "varannoset-delete", obj_uuid],
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")
