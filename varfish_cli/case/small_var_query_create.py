"""Implementation of ``varfish-cli small-var-query-create``"""

import argparse
import json
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import CaseSmallVariantQueryCreateConfig
from varfish_cli.common import CustomEncoder


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("--name", type=str, help="value to set the query name to (if given)")
    parser.add_argument(
        "--public",
        dest="public",
        action="store_true",
        default=False,
        help="Make query public (if given)",
    )
    parser.add_argument(
        "--not-public", dest="public", action="store_false", help="Make query non-public (if given)"
    )
    parser.add_argument("case_uuid", help="UUID of the case to create query for.", type=uuid.UUID)
    parser.add_argument(
        "query_settings", type=str, help="Query settings JSON or path to JSON file with @prefix"
    )


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run create query command."""
    config = CaseSmallVariantQueryCreateConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Creating query")
    base_config = config.case_config.global_config
    case_query = api.CaseQueryV1(
        name=args.name, public=args.public, query_settings=config.query_settings
    )
    query = api.small_var_query_create(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        case_uuid=config.case_uuid,
        case_query=case_query,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    logger.info("All done. Have a nice day!")
    logger.info("Created Query")
    logger.info("=============")
    json.dump(api.CONVERTER.unstructure(query), file, indent="  ", cls=CustomEncoder)
    file.write("\n")
    file.flush()
    logger.info("All done. Have a nice day!")
