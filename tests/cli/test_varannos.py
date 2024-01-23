"""Test CLI for varannos API."""

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
    snapshot: SnapshotAssertion,
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
    assert result.output == snapshot


def test_varannoset_create(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
    snapshot: SnapshotAssertion,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_json = varannoset_list_result_one_elements[0]
    host, token = fake_conn
    m = requests_mock.post(
        f"{host}/varannos/api/varannoset/list-create/{obj_json['project']}",
        json=obj_json,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app,
        ["--verbose", "varannos", "varannoset-create", obj_json["project"], json.dumps(obj_json)],
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == snapshot


def test_varannoset_retrieve(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
    snapshot: SnapshotAssertion,
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
    assert result.output == snapshot


def test_varannoset_update(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
    snapshot: SnapshotAssertion,
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
    assert result.output == snapshot


def test_varannoset_destroy(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannoset_list_result_one_elements,
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


@pytest.fixture
def varannosetentry_list_result_empty() -> typing.List[typing.Any]:
    return []


def test_varannosetentry_list_empty(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannosetentry_list_result_empty,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/varannos/api/varannosetentry/list-create/{project_uuid}",
        json=varannosetentry_list_result_empty,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app, ["--verbose", "varannos", "varannosetentry-list", "--output-format=json", project_uuid]
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == "[]\n"


def test_varannosetentry_create(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannosetentry_list_result_one_elements,
    snapshot: SnapshotAssertion,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_json = varannosetentry_list_result_one_elements[0]
    host, token = fake_conn
    m = requests_mock.post(
        f"{host}/varannos/api/varannosetentry/list-create/{obj_json['varannoset']}",
        json=obj_json,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app,
        [
            "--verbose",
            "varannos",
            "varannosetentry-create",
            obj_json["varannoset"],
            json.dumps(obj_json),
        ],
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == snapshot


@pytest.fixture
def varannosetentry_list_result_one_elements() -> typing.List[typing.Any]:
    with open("tests/cli/data/varannos_varannosetentry-list.len-1.json", "rt") as inputf:
        return json.load(inputf)


def test_varannosetentry_list_one_element(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannosetentry_list_result_one_elements,
    snapshot: SnapshotAssertion,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = str(uuid.uuid4())
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/varannos/api/varannosetentry/list-create/{project_uuid}",
        json=varannosetentry_list_result_one_elements,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app, ["--verbose", "varannos", "varannosetentry-list", "--output-format=json", project_uuid]
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == snapshot


def test_varannosetentry_retrieve(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannosetentry_list_result_one_elements,
    snapshot: SnapshotAssertion,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_json = varannosetentry_list_result_one_elements[0]
    host, token = fake_conn
    m = requests_mock.get(
        f"{host}/varannos/api/varannosetentry/retrieve-update-destroy/{obj_json['sodar_uuid']}",
        json=obj_json,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app, ["--verbose", "varannos", "varannosetentry-retrieve", obj_json["sodar_uuid"]]
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == snapshot


def test_varannosetentry_update(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannosetentry_list_result_one_elements,
    snapshot: SnapshotAssertion,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_json = varannosetentry_list_result_one_elements[0]
    host, token = fake_conn
    m = requests_mock.patch(
        f"{host}/varannos/api/varannosetentry/retrieve-update-destroy/{obj_json['sodar_uuid']}",
        json=obj_json,
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app,
        [
            "--verbose",
            "varannos",
            "varannosetentry-update",
            obj_json["sodar_uuid"],
            json.dumps(obj_json),
        ],
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
    assert result.output == snapshot


def test_varannosetentry_destroy(
    runner: CliRunner,
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    varannosetentry_list_result_one_elements,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    obj_uuid = varannosetentry_list_result_one_elements[0]["sodar_uuid"]
    host, token = fake_conn
    m = requests_mock.delete(
        f"{host}/varannos/api/varannosetentry/retrieve-update-destroy/{obj_uuid}",
        request_headers={"Authorization": f"Token {token}"},
    )
    _ = m
    result = runner.invoke(
        app,
        ["--verbose", "varannos", "varannosetentry-delete", obj_uuid],
    )

    mocker.stopall()

    assert result.exit_code == 0, result.output
