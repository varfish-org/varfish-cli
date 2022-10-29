"""Implementation of ``varfish-cli small-var-query-create``"""

import argparse
import json
import sys
import uuid

from logzero import logger

from varfish_cli import api
from varfish_cli.case.config import CaseSmallVariantQueryShortcut

KEYS = ("inheritance", "frequency", "impact", "quality", "chromosomes", "flags_etc")


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("case_uuid", help="UUID of the case to create query for.", type=uuid.UUID)
    parser.add_argument("quick_preset", help="Quick preset name to use")
    parser.add_argument(
        "--database",
        choices=("refseq", "ensembl"),
        default="refseq",
        help="Transcript database to use, one of refseq (default) and ensembl",
    )
    for key in KEYS:
        parser.add_argument(f"--{key}", help=f"Select in category '{key}'")


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run create query command."""
    config = CaseSmallVariantQueryShortcut.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Creating query")
    base_config = config.case_config.global_config
    res = api.small_var_query_settings_shortcut(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        case_uuid=config.case_uuid,
        database=config.database,
        quick_preset=config.quick_preset,
        **{k: getattr(config, k) for k in KEYS},
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    logger.info("Created Query")
    logger.info("=============")
    json.dump(api.CONVERTER.unstructure(res), file, indent="  ")
    logger.info("All done. Have a nice day!")
