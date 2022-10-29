"""Implementation of ``varfish-cli varannos varannosetentry-retrieve``"""

import argparse
import json
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.varannos.config import VarAnnoSetEntryRetrieveConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "varannosetentry_uuid", help="UUID of the VarAnnoSetEntry to retrieve.", type=uuid.UUID
    )


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run retrieve VarAnnoSetEntry command."""
    config = VarAnnoSetEntryRetrieveConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Retrieving VarAnnoSetEntry")
    base_config = config.varannos_config.global_config
    res = api.varannosetentry_retrieve(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        varannosetentry_uuid=args.varannosetentry_uuid,
        verify_ssl=config.varannos_config.global_config.verify_ssl,
    )
    res_json = api.CONVERTER.unstructure(res)

    logger.info("VarAnnoSetEntry Detail")
    logger.info("=================")
    if config.varannos_config.output_file == "-":
        json.dump(res_json, sys.stdout, indent="  ")
        sys.stdout.write("\n")
        sys.stdout.flush()
    else:
        with open(config.varannos_config.output_file, "wt") as outputf:
            json.dump(res_json, outputf, indent="  ")
            outputf.write("\n")
    logger.info("All done. Have a nice day!")
