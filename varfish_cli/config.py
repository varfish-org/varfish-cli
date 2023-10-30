"""Common configuration code."""

import enum
import os
import tomllib
import typing

import pydantic
from logzero import logger
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
        with open(config_path, "rb") as tomlf:
            try:
                config_toml = tomllib.load(tomlf)
            except tomllib.TOMLDecodeError as e:
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
