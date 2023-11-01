"""Test CLI for importer API."""

import glob
import json
import types
import typing
import uuid

import pytest
from pytest_mock import MockerFixture
from pytest_snapshot.plugin import Snapshot
from requests_mock import ANY
from requests_mock.mocker import Mocker as RequestsMocker
from typer.testing import CliRunner

from tests.conftest import FakeFs
from varfish_cli.cli import app
from varfish_cli.cli.importer import cli_caseimportinfo_create
from varfish_cli.config import CommonOptions


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


def test_caseimportinfo_create_raw_func_call(
    fake_fs_configured: FakeFs,
    requests_mock: RequestsMocker,
    fake_conn: typing.Tuple[str, str],
    caseimportinfo_list_result_two_elements: typing.List[typing.Any],
    snapshot: Snapshot,
    mocker: MockerFixture,
):
    """Test through function call and not runner.

    We create a stubbed out replay of the requests communication and only check
    results against snapshots. This is not much more than a smoke test or a
    change test.
    """
    fake_fs_configured.fs.add_real_directory("tests/data/importer")

    mocker.patch("varfish_cli.config.open", fake_fs_configured.open_, create=True)
    mocker.patch("varfish_cli.config.os", fake_fs_configured.os)

    project_uuid = "5b1d876d-5ea9-426f-9f8f-f82b18830e16"
    host, token = fake_conn
    m_any = requests_mock.register_uri(
        ANY, ANY, request_headers={"Authorization": f"Token {token}"}, json=[]
    )
    m_case_import_info = requests_mock.post(
        f"{host}/importer/api/case-import-info/{project_uuid}/",
        request_headers={"Authorization": f"Token {token}"},
        json=caseimportinfo_list_result_two_elements[0],
    )
    m_case_bam_qc_file = requests_mock.post(
        f"{host}/importer/api/bam-qc-file/8adbf84e-adb2-4c5d-9b5a-2a8194307b79/",
        request_headers={"Authorization": f"Token {token}"},
        json=caseimportinfo_list_result_two_elements[0]["bam_qc_files"][0],
    )
    m_case_variant_set_import_info_create = requests_mock.post(
        f"{host}/importer/api/variant-set-import-info/8adbf84e-adb2-4c5d-9b5a-2a8194307b79/",
        request_headers={"Authorization": f"Token {token}"},
        json=caseimportinfo_list_result_two_elements[0]["variant_sets"][0],
    )
    m_case_genotype_file = requests_mock.post(
        f"{host}/importer/api/genotype-file/104f900b-fa9c-4bd5-a119-35544293fe7f/",
        request_headers={"Authorization": f"Token {token}"},
        json=caseimportinfo_list_result_two_elements[0]["variant_sets"][0]["genotype_files"][0],
    )
    m_case_db_info_file = requests_mock.post(
        f"{host}/importer/api/database-info-file/104f900b-fa9c-4bd5-a119-35544293fe7f/",
        request_headers={"Authorization": f"Token {token}"},
        json=caseimportinfo_list_result_two_elements[0]["variant_sets"][0]["db_info_files"][0],
    )
    m_case_variant_set_import_info_update = requests_mock.put(
        (
            f"{host}/importer/api/variant-set-import-info/8adbf84e-adb2-4c5d-9b5a-2a8194307b79/"
            "104f900b-fa9c-4bd5-a119-35544293fe7f/"
        ),
        request_headers={"Authorization": f"Token {token}"},
        json=caseimportinfo_list_result_two_elements[0]["variant_sets"][0],
    )
    m_case_import_info_update = requests_mock.put(
        (
            f"{host}/importer/api/case-import-info/5b1d876d-5ea9-426f-9f8f-f82b18830e16/"
            "8adbf84e-adb2-4c5d-9b5a-2a8194307b79/"
        ),
        request_headers={"Authorization": f"Token {token}"},
        json=caseimportinfo_list_result_two_elements[0],
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
    cli_caseimportinfo_create(
        ctx=ctx,
        project_uuid=project_uuid,
        paths=list(sorted(glob.glob("tests/data/importer/*"))),
    )

    assert m_any.call_count == 10
    assert m_case_import_info.call_count == 1
    assert m_case_bam_qc_file.call_count == 1
    assert m_case_variant_set_import_info_create.call_count == 2
    assert m_case_genotype_file.call_count == 2
    assert m_case_db_info_file.call_count == 2
    assert m_case_variant_set_import_info_update.call_count == 2
    assert m_case_import_info_update.call_count == 1

    mocker.stopall()
