"""Implementation of ``varfish-cli varannos varannosetentry-update``"""

import argparse
import json
import sys
import uuid

import attrs
from logzero import logger
from typeguard import check_type

from varfish_cli import api
from varfish_cli.api.models import VarAnnoSetEntryV1
from varfish_cli.exceptions import VarFishException
from varfish_cli.varannos.config import VarAnnoSetEntryUpdateConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "varannosetentry_uuid", help="UUID of the var anno set to update.", type=uuid.UUID
    )
    parser.add_argument(
        "field_values",
        metavar="FIELD_VALUE",
        default=[],
        nargs="+",
        help=(
            "Field/value pairs as field=value where value is properly formatted JSON, "
            "e.g., 'title=\"this is a new title\"' on bash with proper escaping."
        ),
    )


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run VarAnnoSetEntry update command."""
    config = VarAnnoSetEntryUpdateConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)

    payload = {}
    cls_fields = dict((field.name, field) for field in attrs.fields(VarAnnoSetEntryV1))
    for field, value in config.field_values:
        if field not in cls_fields:
            raise VarFishException(f"Field {field} is not a valid field in VarAnnoSetEntry")
        else:
            # Check that the decoded JSON fits the typing annotation.
            try:
                check_type(field, value, cls_fields[field].type)
            except TypeError as e:
                raise VarFishException(str(e))
            # Convert dict values to JSON string as this is what the API expects.
            if isinstance(value, dict):
                payload[field] = json.dumps(value)
            else:
                payload[field] = value

    logger.info("Updating VarAnnoSetEntry")
    base_config = config.varannos_config.global_config
    res = api.varannosetentry_update(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        varannosetentry_uuid=args.varannosetentry_uuid,
        payload=payload,
        verify_ssl=config.varannos_config.global_config.verify_ssl,
    )
    res_json = api.CONVERTER.unstructure(res)

    logger.info("VarAnnoSetEntry Detail")
    logger.info("======================")
    if config.varannos_config.output_file == "-":
        json.dump(res_json, sys.stdout, indent="  ")
        sys.stdout.write("\n")
        sys.stdout.flush()
    else:
        with open(config.varannos_config.output_file, "wt") as outputf:
            json.dump(res_json, outputf, indent="  ")
            outputf.write("\n")
    logger.info("All done. Have a nice day!")
