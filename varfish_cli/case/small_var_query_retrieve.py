"""Implementation of ``varfish-cli small-var-query-retrieve``"""

import argparse
import json
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import CaseSmallVariantQueryRetrieveConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("query_uuid", help="UUID of the query to retrieve.", type=uuid.UUID)


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run retrieve query command."""
    config = CaseSmallVariantQueryRetrieveConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Retrieving query")
    base_config = config.case_config.global_config
    res = api.small_var_query_retrieve(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        query_uuid=args.query_uuid,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    logger.info("Query Detail")
    logger.info("============")
    if config.case_config.output_file == "-":
        json.dump(res, sys.stdout, indent="  ")
        sys.stdout.write("\n")
        sys.stdout.flush()
    else:
        with open(config.case_config.output_file, "wt") as outputf:
            json.dump(res, outputf, indent="  ")
            outputf.write("\n")
    logger.info("All done. Have a nice day!")
