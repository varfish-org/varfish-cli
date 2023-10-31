"""Test CLI for varannos API."""

import uuid
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

    assert result.exit_code == 0
    assert result.output == "[]\n"
