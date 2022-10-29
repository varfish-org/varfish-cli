"""Implementation of ``varfish-cli varannos varannosetentry-destroy``"""

import argparse
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.varannos.config import VarAnnoSetEntryRetrieveConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "varannosetentry_uuid", help="UUID of the var anno set to destroy.", type=uuid.UUID
    )


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run destroy VarAnnoSetEntry command."""
    config = VarAnnoSetEntryRetrieveConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Destroying VarAnnoSetEntry")
    base_config = config.varannos_config.global_config
    api.varannosetentry_destroy(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        varannosetentry_uuid=args.varannosetentry_uuid,
        verify_ssl=config.varannos_config.global_config.verify_ssl,
    )
    logger.info("All done. Have a nice day!")
