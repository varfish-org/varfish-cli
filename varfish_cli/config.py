"""Common configuration code."""

import enum
import os
import uuid

try:
    import tomllib
    from tomllib import TOMLDecodeError
except ImportError:
    import toml as tomllib
    from toml import TomlDecodeError as TOMLDecodeError

import typing

from logzero import logger
import pydantic
import typer


class CommonOptions(pydantic.BaseModel):
    """Shared options for all subcommands."""

    #: Whether verbose output is enabled.
    verbose: bool = False
    #: Whether to verify SSL.
    verify_ssl: bool = True
    #: Path to configuration file.
    config: typing.Optional[str] = None
    #: VarFish server URL key to use.
    varfish_server_url: typing.Optional[str] = None
    #: VarFish API token to use.
    varfish_api_token: typing.Optional[pydantic.SecretStr] = None


def load_config(config_path: str) -> typing.Tuple[typing.Optional[str], typing.Optional[str]]:
    """Load configuration and return server URL and API token.

    :returns: Tuple of ``(server_url, api_token)``
    """
    config_path = os.path.expanduser(os.path.expandvars(config_path))

    toml_varfish_server_url: typing.Optional[str] = None
    toml_varfish_api_token: typing.Optional[str] = None

    if not os.path.exists(config_path):
        logger.info("could not find configuration file %s.", config_path)
    else:
        logger.debug("loading configuration from %s", config_path)
        with open(config_path, "rt") as tomlf:
            try:
                config_toml = tomllib.loads(tomlf.read())
            except TOMLDecodeError as e:
                logger.error("could not parse configuration file %s: %s", config_path, e)
                raise typer.Exit(1)
            toml_varfish_server_url = config_toml.get("global", {}).get("varfish_server_url")
            if toml_varfish_server_url:
                logger.debug("using global/varfish_server_url from %s", config_path)
            else:
                logger.debug("global/varfish_server_url not set in %s", config_path)
            toml_varfish_api_token = config_toml.get("global", {}).get("varfish_api_token")
            if toml_varfish_api_token:
                logger.debug("using global/varfish_server_url from %s", config_path)
            else:
                logger.debug("global/varfish_api_token not set in %s", config_path)

    return toml_varfish_server_url, toml_varfish_api_token


@enum.unique
class ImportDataProtocol(enum.Enum):
    """Protocol for importing data."""

    S3 = "s3"
    HTTP = "http"
    HTTPS = "https"
    FILE = "file"


class ProjectConfig(pydantic.BaseModel):
    """Configuration for one project in ``~/.varfishrc.toml``."""

    #: Human-readable name of the project.
    title: typing.Optional[str] = None
    #: UUID of project.
    uuid: uuid.UUID
    #: Protocol to use.
    import_data_protocol: ImportDataProtocol
    #: Host name to use.
    import_data_host: typing.Optional[str] = None
    #: Path prefix to use.
    import_data_path: str
    #: User name to use for connecting, if any.
    import_data_user: typing.Optional[str] = None
    #: Password to use for connecting, if any.
    import_data_password: typing.Optional[pydantic.SecretStr] = None

    @pydantic.field_serializer("import_data_password", when_used="json")
    def dump_secret(self, v: typing.Optional[pydantic.SecretStr]):
        if v:
            return v.get_secret_value()
        else:
            return v


def load_projects(config_path: str) -> typing.Dict[uuid.UUID, ProjectConfig]:
    """Load projects from configuration TOML file at ``config_path``"""

    with open(config_path, "rt") as inputf:
        fcontents = inputf.read()
    toml_dict = tomllib.loads(fcontents)

    projects = list(map(ProjectConfig.model_validate, toml_dict.get("projects", [])))
    return {p.uuid: p for p in projects}
