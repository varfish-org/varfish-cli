import json
import typing
import uuid

import pytest
from pytest_mock import MockerFixture
from pytest_snapshot.plugin import Snapshot
from requests_mock.mocker import Mocker as RequestsMocker
from typer.testing import CliRunner

from tests.conftest import FakeFs
from varfish_cli import common


def test_load_project_config(
    fake_fs_configured_projects: FakeFs,
    mocker: MockerFixture,
    snapshot: Snapshot,
):
    mocker.patch("varfish_cli.common.open", fake_fs_configured_projects.open_, create=True)
    mocker.patch("varfish_cli.common.os", fake_fs_configured_projects.os)

    config_null = common.load_project_config(uuid.UUID("00000000-0000-0000-0000-000000000000"))
    config_some = common.load_project_config(uuid.UUID("00000000-0000-0000-0000-000000000001"))

    mocker.stopall()

    assert config_null is None
    snapshot.assert_match(
        json.dumps(config_some.model_dump(mode="json"), indent=2), "configuration"
    )
