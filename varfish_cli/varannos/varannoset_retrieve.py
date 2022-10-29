"""Implementation of ``varfish-cli varannos varannoset-retrieve``"""

import argparse
import json
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.varannos.config import VarAnnoSetRetrieveConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "varannoset_uuid", help="UUID of the var anno set to retrieve.", type=uuid.UUID
    )


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run retrieve VarAnnoSet command."""
    config = VarAnnoSetRetrieveConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Retrieving VarAnnoSet")
    base_config = config.varannos_config.global_config
    res = api.varannoset_retrieve(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        varannoset_uuid=args.varannoset_uuid,
        verify_ssl=config.varannos_config.global_config.verify_ssl,
    )
    res_json = api.CONVERTER.unstructure(res)

    logger.info("VarAnnoSet Detail")
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
