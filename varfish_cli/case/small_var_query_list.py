"""Implementation of ``varfish-cli small-var-query-list``"""

import argparse
import sys
import typing
import uuid

import attrs
from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import CaseSmallVariantQueryListConfig, OutputFormat
from varfish_cli.common import tabular_output, write_output

#: The default fields by output format.
DEFAULT_FIELDS: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE: (
        "sodar_uuid",
        "date_created",
        "case",
        "user",
        "form_id",
        "form_version",
        "name",
        "public",
    ),
    OutputFormat.CSV: None,
    OutputFormat.JSON: None,
}


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("case_uuid", help="UUID of the case to list queries for.", type=uuid.UUID)


def run(case_config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run list query command."""
    case_config = attrs.evolve(
        case_config,
        output_fields=case_config.output_fields or DEFAULT_FIELDS.get(case_config.output_format),
    )
    config = CaseSmallVariantQueryListConfig.create(args, case_config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing queries")
    base_config = config.case_config.global_config
    res = api.small_var_query_list(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        case_uuid=args.case_uuid,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    logger.info("Generating output")
    header = (
        case_config.output_fields
        if case_config.output_fields
        else [f.name for f in attrs.fields(api.CaseQueryResultV1)]
    )
    output = tabular_output(values=res, header=header)

    logger.info("Writing output")
    logger.info("==============")
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
