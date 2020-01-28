"""Implementation of varfish-cli subcommand."""

import argparse

from .config import CaseConfig
from .list import setup_argparse as setup_argparse_list
from ..common import run_nocmd


def setup_argparse(parser: argparse.ArgumentParser) -> None:
    """Main entry point for subcommand."""
    subparsers = parser.add_subparsers(dest="case_cmd")

    setup_argparse_list(subparsers.add_parser("list", help="List cases."))


def run(config, toml_config, args, parser, subparser):
    """Main entry point for case command."""
    if not args.case_cmd:  # pragma: nocover
        return run_nocmd(config, args, parser, subparser)
    else:
        config = CaseConfig.create(args, config, toml_config)
        return args.case_cmd(config, toml_config, args, parser, subparser)
