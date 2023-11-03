import json

from pytest_snapshot.plugin import Snapshot

from varfish_cli import config


def test_load_config():
    result = config.load_config("tests/data/config/varfishrc.toml")
    assert result == ("https://varfish.example.com/", "39c01db5-a808-4262-8b4d-7fd712389b59")


def test_load_projects(snapshot: Snapshot):
    result = config.load_projects("tests/data/config/varfishrc.projects.toml")
    assert len(result) == 4
    result_str = json.dumps([obj.model_dump(mode="json") for obj in result.values()], indent=2)
    snapshot.assert_match(result_str, "result")
