"""Implementation of varfish-cli subcommand 'projects'."""

import argparse
import typing

import attr

from varfish_cli.common import CommonConfig, OutputFormat, run_nocmd
from varfish_cli.projects.project_list import (
    setup_argparse as setup_argparse_project_list,
)


@attr.s(frozen=True, auto_attribs=True)
class ProjectsConfig:
    """Configuration for the ``varfish-cli project`` command."""

    #: Global configuration
    global_config: CommonConfig

    #: Path to output file
    output_file: str = "-"

    #: Output format
    output_format: OutputFormat = OutputFormat.TABLE

    #: delimiter for CSV output
    output_delimiter: str = ","

    #: Fields to use for output.
    output_fields: typing.Optional[typing.List[str]] = []

    @staticmethod
    def create(args, global_config, toml_config=None):
        _ = toml_config
        return ProjectsConfig(
            output_format=OutputFormat(args.output_format),
            output_file=args.output_file,
            output_delimiter=args.output_delimiter,
            output_fields=args.output_fields.split(",") if args.output_fields else [],
            global_config=global_config,
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

    subparsers = parser.add_subparsers(dest="projects_cmd")
    setup_argparse_project_list(subparsers.add_parser("project-list", help="List project objects."))


def run(config, toml_config, args, parser, subparser):
    """Main entry point for project command."""
    if not args.projects_cmd:  # pragma: nocover
        return run_nocmd(config, args, parser, subparser)
    else:
        config = ProjectsConfig.create(args, config, toml_config)
        print(args.projects_cmd)
        return args.projects_cmd(config, toml_config, args, parser, subparser)
