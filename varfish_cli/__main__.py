"""Main entry point for VarFish CLI."""

import argparse
import logging
import os
import sys

import logzero
import attr
import toml
from logzero import logger

from varfish_cli import __version__
from .common import run_nocmd
from .subcommand import setup_argparse as setup_argparse_subcommand
from .subcommand import run as run_subcommand

#: Paths to search the global configuration in.
GLOBAL_CONFIG_PATHS = ("~/.varfishrc.toml",)


@attr.s(frozen=True, auto_attribs=True)
class Config:
    """Common configuration for all commands."""

    #: API key to use for VarFish.
    varfish_api_key: str = attr.ib(repr=lambda value: repr(value[:4] + (len(value) - 4) * "*"))

    #: Base URL to VarFish server.
    varfish_server_url: str

    @classmethod
    def create(cls, args, toml_config=None):
        toml_config = toml_config or {}
        return Config(
            varfish_api_key=(
                args.varfish_api_key or toml_config.get("global", {})["varfish_api_key"]
            ),
            varfish_server_url=(
                args.varfish_server_url or toml_config.get("global", {})["varfish_server_url"]
            ),
        )


def setup_argparse_only():  # pragma: nocover
    """Wrapper for ``setup_argparse()`` that only returns the parser.

    Only used in sphinx documentation via ``sphinx-argparse``.
    """
    return setup_argparse()[0]


def setup_argparse():
    """Create argument parser."""
    # Construct argument parser and set global options.
    parser = argparse.ArgumentParser(prog="varfish-cli")
    parser.add_argument("--verbose", action="store_true", default=False, help="Increase verbosity.")
    parser.add_argument("--version", action="version", version="%%(prog)s %s" % __version__)

    group = parser.add_argument_group("Basic Configuration")
    group.add_argument(
        "--config",
        default=os.environ.get("VARFISH_CONFIG_PATH", None),
        help="Path to configuration file.",
    )
    group.add_argument(
        "--varfish-server-url",
        default=os.environ.get("VARFISH_SERVER_URL", None),
        help="VarFish server URL key to use, defaults to env VARFISH_SERVER_URL.",
    )
    group.add_argument(
        "--varfish-api-key",
        default=os.environ.get("VARFISH_API_KEY", None),
        help="VarFish API key to use, defaults to env VARFISH_API_KEY.",
    )

    # Add sub parsers for each argument.
    subparsers = parser.add_subparsers(dest="cmd")

    setup_argparse_subcommand(subparsers.add_parser("subcommand", help="Subcommand description."))

    return parser, subparsers


def main(argv=None):
    """Main entry point before parsing command line arguments."""
    # Setup command line parser.
    parser, subparsers = setup_argparse()

    # Actually parse command line arguments.
    args = parser.parse_args(argv)

    # Load configuration, if any.
    if args.config:
        config_paths = (args.config,)
    else:
        config_paths = GLOBAL_CONFIG_PATHS
    for config_path in config_paths:
        config_path = os.path.expanduser(os.path.expandvars(config_path))
        if os.path.exists(config_path):
            with open(config_path, "rt") as tomlf:
                toml_config = toml.load(tomlf)
            break
    else:
        toml_config = None
        logger.info("Could not find any of the global configuration files %s.", config_paths)

    # Merge configuration from command line/environment args and configuration file.
    config = Config.create(args, toml_config)

    # Setup logging verbosity.
    if args.verbose:  # pragma: no cover
        level = logging.DEBUG
    else:
        level = logging.INFO
    logzero.loglevel(level=level)

    # Handle the actual command line.
    cmds = {None: run_nocmd, "subcommand": run_subcommand}

    logger.info("Configuration: %s", config)

    res = cmds[args.cmd](config, args, parser, subparsers.choices[args.cmd] if args.cmd else None)
    if not res:
        logger.info("All done. Have a nice day!")
    else:  # pragma: nocover
        logger.error("Something did not work out correctly.")
    return res


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
