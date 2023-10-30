"""Implementation of varfish-cli subcommand 'varannos'."""

import argparse

from varfish_cli.common import run_nocmd
from varfish_cli.varannos.config import OutputFormat, VarannosConfig
from varfish_cli.varannos.varannoset_destroy import (
    setup_argparse as setup_argparse_varannoset_destroy,
)
from varfish_cli.varannos.varannoset_list import (
    setup_argparse as setup_argparse_varannoset_list,
)
from varfish_cli.varannos.varannoset_retrieve import (
    setup_argparse as setup_argparse_varannoset_retrieve,
)
from varfish_cli.varannos.varannoset_update import (
    setup_argparse as setup_argparse_varannoset_update,
)
from varfish_cli.varannos.varannosetentry_destroy import (
    setup_argparse as setup_argparse_varannosetentry_destroy,
)
from varfish_cli.varannos.varannosetentry_list import (
    setup_argparse as setup_argparse_varannosetentry_list,
)
from varfish_cli.varannos.varannosetentry_retrieve import (
    setup_argparse as setup_argparse_varannosetentry_retrieve,
)
from varfish_cli.varannos.varannosetentry_update import (
    setup_argparse as setup_argparse_varannosetentry_update,
)


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
    setup_argparse_varannoset_list(
        subparsers.add_parser("varannoset-list", help="List varannoset objects.")
    )
    setup_argparse_varannoset_retrieve(
        subparsers.add_parser("varannoset-retrieve", help="Retrieve varannoset object.")
    )
    setup_argparse_varannoset_update(
        subparsers.add_parser("varannoset-update", help="Update varannoset object.")
    )
    setup_argparse_varannoset_destroy(
        subparsers.add_parser("varannoset-destroy", help="Destroy varannoset object.")
    )
    setup_argparse_varannosetentry_list(
        subparsers.add_parser("varannosetentry-list", help="List varannosetentry objects.")
    )
    setup_argparse_varannosetentry_retrieve(
        subparsers.add_parser("varannosetentry-retrieve", help="Retrieve varannosetentry object.")
    )
    setup_argparse_varannosetentry_update(
        subparsers.add_parser("varannosetentry-update", help="Update varannosetentry object.")
    )
    setup_argparse_varannosetentry_destroy(
        subparsers.add_parser("varannosetentry-destroy", help="Destroy varannosetentry object.")
    )


def run(config, toml_config, args, parser, subparser):
    """Main entry point for case command."""
    if not args.case_cmd:  # pragma: nocover
        return run_nocmd(config, args, parser, subparser)
    else:
        config = VarannosConfig.create(args, config, toml_config)
        return args.case_cmd(config, toml_config, args, parser, subparser)
