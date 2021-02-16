from types import SimpleNamespace

from varfish_cli.common import CommonConfig
from varfish_cli.case import config

import pytest


@pytest.fixture
def args():
    return SimpleNamespace(
        verbose=False,
        verify_ssl=True,
        varfish_api_token="XXX",
        varfish_server_url="https://varfish.example.com/",
        project_uuid="123",
        owner="456",
        paths=["x", "y"],
        strip_family_regex="regex",
        case_name_suffix="suffix",
        resubmit=True,
        force_fresh=False,
    )


@pytest.fixture
def common_config(args):
    return CommonConfig.create(args)


@pytest.fixture
def case_config(args, common_config):
    return config.CaseConfig.create(args, common_config)


def test_create_case_list_config(args, case_config):
    config.CaseListConfig.create(args, case_config)


def test_case_list_import_info_config(args, case_config):
    config.CaseListImportInfoConfig.create(args, case_config)


def test_case_create_import_info_config(args, case_config):
    config.CaseCreateImportInfoConfig.create(args, case_config, args.strip_family_regex)
