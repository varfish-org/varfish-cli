"""Implementation of ``varfish-cli small-var-query-fetch-results``"""

import argparse
import sys
import typing
import uuid

import attrs
from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import (
    CaseSmallVariantQueryFetchResultsConfig,
    OutputFormat,
)
from varfish_cli.common import tabular_output, write_output

#: The default output fields.
DEFAULT_OUTPUT_FIELDS = (
    "release",
    "chromosome",
    "start",
    "reference",
    "alternative",
    "var_type",
    "info",
    "refseq_effect",
    "refseq_gene_id",
    "refseq_transcript_id",
    "genotype",
)

#: The default fields by output format.
DEFAULT_FIELDS: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE: DEFAULT_OUTPUT_FIELDS,
    OutputFormat.CSV: DEFAULT_OUTPUT_FIELDS,
    OutputFormat.JSON: DEFAULT_OUTPUT_FIELDS,
}


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "query_uuid", help="UUID of the query to fetch results for.", type=uuid.UUID
    )


def run(case_config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run fetch results command."""
    case_config = attrs.evolve(
        case_config,
        output_fields=case_config.output_fields or DEFAULT_FIELDS.get(case_config.output_format),
    )
    config = CaseSmallVariantQueryFetchResultsConfig.create(args, case_config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Fetching results")
    base_config = config.case_config.global_config
    res = api.small_var_query_fetch_results(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        query_uuid=args.query_uuid,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    header = (
        case_config.output_fields
        if case_config.output_fields
        else [f.name for f in attrs.fields(api.CaseQueryResultV1)]
    )
    output = tabular_output(values=res, header=header)

    logger.info("Query Results")
    logger.info("============")
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
