"""Implementation of ``varfish-cli varannos varannoset-list``"""

import argparse
import sys
import typing
import uuid

import attrs
from logzero import logger

from varfish_cli import api
from varfish_cli.common import tabular_output, write_output
from varfish_cli.varannos.config import OutputFormat, VarAnnoSetListConfig

#: The default fields by output format.
DEFAULT_FIELDS: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE: (
        "sodar_uuid",
        "date_modified",
        "project",
        "title",
        "release",
        "fields",
    ),
    OutputFormat.CSV: None,
    OutputFormat.JSON: None,
}


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "project_uuid", help="UUID of the project to list varannoset objects for.", type=uuid.UUID
    )


def run(varannos_config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run VarAnnoSet list command."""
    varannos_config = attrs.evolve(
        varannos_config,
        output_fields=varannos_config.output_fields
        or DEFAULT_FIELDS.get(varannos_config.output_format),
    )
    config = VarAnnoSetListConfig.create(args, varannos_config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing VarAnnoSets")
    base_config = config.varannos_config.global_config
    res = api.varannoset_list(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        project_uuid=args.project_uuid,
        verify_ssl=config.varannos_config.global_config.verify_ssl,
    )

    logger.info("Generating output")
    header = (
        varannos_config.output_fields
        if varannos_config.output_fields
        else [f.name for f in attrs.fields(api.VarAnnoSetV1)]
    )
    output = tabular_output(values=res, header=header)

    logger.info("Writing output")
    logger.info("==============")
    if config.varannos_config.output_file == "-":
        write_output(
            output,
            sys.stdout,
            config.varannos_config.output_format,
            config.varannos_config.output_delimiter,
        )
    else:
        with open(config.varannos_config.output_file, "wt") as outputf:
            write_output(
                output,
                outputf,
                config.varannos_config.output_format,
                config.varannos_config.output_delimiter,
            )
    logger.info("All done. Have a nice day!")
