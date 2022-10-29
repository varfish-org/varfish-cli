"""Implementation of ``varfish-cli case list``."""

import argparse
import json
import sys
import typing
import uuid

import attrs
from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import CaseListConfig, OutputFormat
from varfish_cli.common import tabular_output, write_output

#: The default fields to use for output.
DEFAULT_FIELDS: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE: ("sodar_uuid", "name", "index", "members"),
    OutputFormat.CSV: None,
    OutputFormat.JSON: None,
}


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("project_uuid", help="UUID of the project to get.", type=uuid.UUID)


def run(case_config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run case list command."""
    case_config = attrs.evolve(
        case_config,
        output_fields=case_config.output_fields or DEFAULT_FIELDS.get(case_config.output_format),
    )
    config = CaseListConfig.create(args, case_config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing cases")
    base_config = config.case_config.global_config
    res = api.case_list(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        project_uuid=config.project_uuid,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    def format_member(case):
        value = []
        for member in case.pedigree:
            value.append(
                {k: getattr(member, k) for k in ("name", "father", "mother", "sex", "affected")}
            )
        if case_config.output_format == OutputFormat.TABLE:
            return json.dumps(value, indent=" ")
        else:
            return value

    logger.info("Generating output")
    header = (
        case_config.output_fields
        if case_config.output_fields
        else [f.name for f in attrs.fields(api.Case)]
    )
    header = [{"pedigree": "members"}.get(v, v) for v in header]  # pedigree => members, rest same
    output = tabular_output(values=res, header=header, field_formatters={"members": format_member})

    logger.info("Writing output")
    if config.case_config.output_file == "-":
        write_output(
            output,
            sys.stdout,
            config.case_config.output_format,
            config.case_config.output_delimiter,
        )
    else:
        with open(config.case_config.output_file, "wt") as outputf:
            write_output(
                output,
                outputf,
                config.case_config.output_format,
                config.case_config.output_delimiter,
            )

    logger.info("All done. Have a nice day!")
