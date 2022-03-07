"""Implementation of ``varfish-cli small-var-query-list``"""
import argparse
import json
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import CaseSmallVariantQueryListConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("case_uuid", help="UUID of the case to list queries for.", type=uuid.UUID)


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run list query command."""
    config = CaseSmallVariantQueryListConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing queries")
    base_config = config.case_config.global_config
    res = api.small_var_query_list(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        case_uuid=args.case_uuid,
    )

    print("Query List", file=file)
    print("==========", file=file)
    print(file=file)
    json.dump(res, file, indent="  ")
