"""Implementation of ``varfish-cli projects project-list``"""

import argparse
import sys
import typing

import attrs
from logzero import logger

from varfish_cli import api
from varfish_cli.common import tabular_output, write_output
from varfish_cli.projects.config import OutputFormat, ProjectsListConfig

#: The default fields by output format.
DEFAULT_FIELDS: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE: (
        "sodar_uuid",
        "type",
        "title",
    ),
    OutputFormat.CSV: None,
    OutputFormat.JSON: None,
}


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="projects_cmd", default=run, help=argparse.SUPPRESS)


def run(projects_config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run Project list command."""
    projects_config = attrs.evolve(
        projects_config,
        output_fields=projects_config.output_fields
        or DEFAULT_FIELDS.get(projects_config.output_format),
    )
    config = ProjectsListConfig.create(args, projects_config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing Projects")
    base_config = config.projects_config.global_config
    res = api.project_list(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        verify_ssl=config.projects_config.global_config.verify_ssl,
    )

    logger.info("Generating output")
    header = (
        projects_config.output_fields
        if projects_config.output_fields
        else [f.name for f in attrs.fields(api.Project)]
    )
    output = tabular_output(values=res, header=header)

    logger.info("Writing output")
    logger.info("==============")
    if config.projects_config.output_file == "-":
        write_output(
            output,
            sys.stdout,
            config.projects_config.output_format,
            config.projects_config.output_delimiter,
        )
    else:
        with open(config.projects_config.output_file, "wt") as outputf:
            write_output(
                output,
                outputf,
                config.projects_config.output_format,
                config.projects_config.output_delimiter,
            )
    logger.info("All done. Have a nice day!")
