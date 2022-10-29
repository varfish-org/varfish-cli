"""Implementation of varfish-cli subcommand 'case'."""

import argparse

from varfish_cli.case.config import CaseConfig, OutputFormat
from varfish_cli.case.create_case_import import (
    setup_argparse as setup_argparse_create_import,
)
from varfish_cli.case.list_case import setup_argparse as setup_argparse_list
from varfish_cli.case.list_case_import import (
    setup_argparse as setup_argparse_list_import,
)
from varfish_cli.case.small_var_query_create import (
    setup_argparse as setup_argparse_small_var_query_create,
)
from varfish_cli.case.small_var_query_fetch_results import (
    setup_argparse as setup_argparse_small_var_query_fetch_results,
)
from varfish_cli.case.small_var_query_list import (
    setup_argparse as setup_argparse_small_var_query_list,
)
from varfish_cli.case.small_var_query_retrieve import (
    setup_argparse as setup_argparse_small_var_query_retrieve,
)
from varfish_cli.case.small_var_query_settings_shortcut import (
    setup_argparse as setup_argparse_small_var_query_settings_shortcut,
)
from varfish_cli.case.small_var_query_status import (
    setup_argparse as setup_argparse_small_var_query_status,
)
from varfish_cli.case.small_var_query_update import (
    setup_argparse as setup_argparse_small_var_query_update,
)
from varfish_cli.common import run_nocmd


def setup_argparse(parser: argparse.ArgumentParser) -> None:
    """Main entry point for subcommand."""
    of_choices = [o.value for o in OutputFormat]
    of_default = OutputFormat.TABLE.value
    parser.add_argument(
        "--output-format",
        help=f"Output format, one of {of_choices}, default: {of_default}",
        choices=of_choices,
        default=of_default,
    )
    parser.add_argument("--output-fields", help="Output fields if non-default ones")
    parser.add_argument(
        "--output-delimiter", help="Separator for CSV output, default: ','", default=","
    )
    parser.add_argument(
        "--output-file", help="Path to file to write to, defaults to stdout", default="-"
    )

    subparsers = parser.add_subparsers(dest="case_cmd")
    setup_argparse_list(subparsers.add_parser("list", help="List cases."))
    setup_argparse_list_import(
        subparsers.add_parser("list-import-info", help="List case import infos.")
    )
    setup_argparse_create_import(
        subparsers.add_parser("create-import-info", help="Create case import infos.")
    )
    setup_argparse_small_var_query_create(
        subparsers.add_parser("small-var-query-create", help="Create small var query")
    )
    setup_argparse_small_var_query_fetch_results(
        subparsers.add_parser("small-var-query-fetch-results", help="Fetch small var query results")
    )
    setup_argparse_small_var_query_list(
        subparsers.add_parser("small-var-query-list", help="List small var queries")
    )
    setup_argparse_small_var_query_retrieve(
        subparsers.add_parser("small-var-query-retrieve", help="Retrieve small variant query")
    )
    setup_argparse_small_var_query_status(
        subparsers.add_parser("small-var-query-status", help="Get small variant query status")
    )
    setup_argparse_small_var_query_update(
        subparsers.add_parser("small-var-query-update", help="Update small variant query")
    )
    setup_argparse_small_var_query_settings_shortcut(
        subparsers.add_parser(
            "small-var-query-shortcut", help="Generate query parameters from shortcut"
        )
    )


def run(config, toml_config, args, parser, subparser):
    """Main entry point for case command."""
    if not args.case_cmd:  # pragma: nocover
        return run_nocmd(config, args, parser, subparser)
    else:
        config = CaseConfig.create(args, config, toml_config)
        return args.case_cmd(config, toml_config, args, parser, subparser)
