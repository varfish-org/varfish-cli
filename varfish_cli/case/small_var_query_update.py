"""Implementation of ``varfish-cli small-var-query-update``"""

import argparse
import json
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import CaseSmallVariantQueryUpdateConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("--name", type=str, help="value to set the query name to (if given)")
    parser.add_argument(
        "--public",
        dest="public",
        action="store_true",
        default=None,
        help="Make query public (if given)",
    )
    parser.add_argument(
        "--not-public", dest="public", action="store_false", help="Make query non-public (if given)"
    )
    parser.add_argument("query_uuid", help="UUID of the query to update.", type=uuid.UUID)


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run query update command."""
    config = CaseSmallVariantQueryUpdateConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Updating query")
    base_config = config.case_config.global_config
    case_query = api.CaseQueryV1(name=args.name, public=args.public)
    res = api.small_var_query_update(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        query_uuid=args.query_uuid,
        case_query=case_query,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    print("Updated Query", file=file)
    print("=============", file=file)
    json.dump(res, file, indent="  ")
    print(file=file)
    file.flush()
