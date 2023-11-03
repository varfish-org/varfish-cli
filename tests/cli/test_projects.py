"""Test CLI for projects API."""

import json
import types
import typing
import uuid

import pytest
from pytest_mock import MockerFixture
from pytest_snapshot.plugin import Snapshot
from requests_mock.mocker import Mocker as RequestsMocker
from typer.testing import CliRunner

from tests.conftest import FakeFs
from varfish_cli.cli import app
from varfish_cli.cli.projects import cli_project_load_config
from varfish_cli.config import CommonOptions


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

    assert result.exit_code == 0, result.output
    snapshot.assert_match(result.output, "result_output")


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
    snapshot: Snapshot,
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
    snapshot.assert_match(result.output, "result_output")


def test_project_load_config_raw_func_call(
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)
    mocker.patch("varfish_cli.cli.projects.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.cli.projects.os", fake_fs_configured.os, create=True)

    responses = {
        "import_data_host": ("STRING", "http-host.example.com"),
        "import_data_password": ("STRING", "http-password"),
        "import_data_path": ("STRING", "http-prefix/"),
        "import_data_port": ("INTEGER", 80),
        "import_data_protocol": ("STRING", "http"),
        "import_data_user": ("STRING", "http-user"),
    }

    project_uuid = "16251f30-1168-41c9-8af6-07c8f40f6860"
    host, token = fake_conn
    req_mocks = []
    for setting_name, (setting_type, setting_value) in responses.items():
        req_mocks.append(
            requests_mock.get(
                (
                    f"{host}/project/api/settings/retrieve/{project_uuid}?app_name=cases_import"
                    f"&setting_name={setting_name}"
                ),
                request_headers={"Authorization": f"Token {token}"},
                json={
                    "project": project_uuid,
                    "user": None,
                    "name": setting_name,
                    "type": setting_type,
                    "value": setting_value,
                    "user_modifiable": True,
                    "app_name": "cases_import",
                },
            )
        )

    ctx = types.SimpleNamespace(
        obj=CommonOptions(
            verbose=True,
            verify_ssl=False,
            config=None,
            varfish_server_url=host,
            varfish_api_token=token,
        )
    )
    cli_project_load_config(
        ctx,
        project_uuid=project_uuid,
        config_path=fake_fs_configured.os.path.expanduser("~/.varfishrc.toml"),
    )

    rc_path = fake_fs_configured.os.path.expanduser("~/.varfishrc.toml")
    with fake_fs_configured.open_(rc_path, "rt") as inputf:
        fcontents = inputf.read()

    mocker.stopall()

    for req_mock in req_mocks:
        assert req_mock.called_once, req_mock._netloc

    snapshot.assert_match(fcontents, "result_output")
