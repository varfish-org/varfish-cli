import typing

import attrs
from pyfakefs import fake_filesystem, fake_open, fake_os
import pytest
from typer.testing import CliRunner


@attrs.frozen
class FakeFs:
    """Wrapper for fake filesystem to circumvent automatic patching.

    Bundled with the fake OS moduel and file ``open``.
    """

    #: Fake file system.
    fs: fake_filesystem.FakeFilesystem
    #: Fake OS module.
    os: fake_filesystem.FakeOsModule
    #: Fake open module.
    open_: fake_filesystem.FakeFileOpen


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def fake_fs() -> FakeFs:
    """Fake file system bundle."""
    fs = fake_filesystem.FakeFilesystem()
    return FakeFs(fs=fs, os=fake_os.FakeOsModule(fs), open_=fake_open.FakeFileOpen(fs))


@pytest.fixture
def fake_fs_empty_config(fake_fs: FakeFs) -> FakeFs:
    """Fake file system with empty ``~/.varfishrc.toml``"""
    return fake_fs


@pytest.fixture
def fake_conn() -> typing.Tuple[str, str]:
    return ("http://varfish.example.com:8080", "faKeTOKeN")


@pytest.fixture
def fake_fs_configured(fake_fs: FakeFs, fake_conn: typing.Tuple[str, str]) -> FakeFs:
    """Fake file system with minimal ``~/.varfishrc.toml``"""
    host, token = fake_conn
    conf_file_path = fake_fs.os.path.expanduser("~/.varfishrc.toml")
    fake_fs.fs.create_file(
        conf_file_path,
        contents="\n".join(
            [
                "[global]",
                f'varfish_server_url = "{host}"',
                f'varfish_api_token = "{token}"',
            ]
        )
        + "\n",
    )
    return fake_fs


@pytest.fixture
def fake_fs_configured_projects(fake_fs: FakeFs, fake_conn: typing.Tuple[str, str]) -> FakeFs:
    """Fake file system with ``~/.varfishrc.toml`` that also has project config"""
    host, token = fake_conn
    conf_file_path = fake_fs.os.path.expanduser("~/.varfishrc.toml")
    fake_fs.fs.create_file(
        conf_file_path,
        contents="\n".join(
            [
                "[global]",
                f'varfish_server_url = "{host}"',
                f'varfish_api_token = "{token}"',
                "",
                "[[projects]]",
                'title = "S3 Example"',
                'uuid = "00000000-0000-0000-0000-000000000001"',
                'import_data_protocol = "s3"',
                'import_data_host = "s3-server.example.net"',
                "import_data_port = 443",
                'import_data_path = "bucket-name"',
                'import_data_user = "s3-user"',
                'import_data_password = "s3-key"',
            ]
        )
        + "\n",
    )
    return fake_fs
