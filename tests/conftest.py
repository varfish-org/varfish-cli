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
    """Fake file system with filled ``~/.varfishrc.toml``"""
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
