"""Implementation of varfish-cli subcommand."""

import argparse

from .config import CaseConfig
from .list_case import setup_argparse as setup_argparse_list
from .list_case_import import setup_argparse as setup_argparse_list_import
from .create_case_import import setup_argparse as setup_argparse_create_import
from ..common import run_nocmd


def setup_argparse(parser: argparse.ArgumentParser) -> None:
    """Main entry point for subcommand."""
    subparsers = parser.add_subparsers(dest="case_cmd")

    setup_argparse_list(subparsers.add_parser("list", help="List cases."))
    setup_argparse_list_import(
        subparsers.add_parser("list-import-info", help="List case import infos.")
    )
    setup_argparse_create_import(
        subparsers.add_parser("create-import-info", help="Create case import infos.")
    )


def run(config, toml_config, args, parser, subparser):
    """Main entry point for case command."""
    if not args.case_cmd:  # pragma: nocover
        return run_nocmd(config, args, parser, subparser)
    else:
        config = CaseConfig.create(args, config, toml_config)
        return args.case_cmd(config, toml_config, args, parser, subparser)
