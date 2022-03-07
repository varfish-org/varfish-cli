"""Implementation of ``varfish-cli case list-import-info.``"""

import argparse
import sys
import uuid

from logzero import logger

from .. import api
from .config import CaseListImportInfoConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "--owner", default=None, help="Optionally, user name to return case import infos for."
    )
    parser.add_argument("project_uuid", help="UUID of the project to get.", type=uuid.UUID)


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run case list import command."""
    config = CaseListImportInfoConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing cases")
    base_config = config.case_config.global_config
    res = api.case_import_info_list(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        project_uuid=config.project_uuid,
        owner=config.owner,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    print("Case Import Info List", file=file)
    print("=====================", file=file)
    print(file=file)
    for info in res:
        print("- uuid: %s" % repr(str(info.sodar_uuid)), file=file)
        print("  owner: %s" % repr(info.release.value), file=file)
        print("  owner: %s" % repr(info.owner), file=file)
        print("  name: %s" % repr(info.name), file=file)
        print("  index: %s" % repr(info.index), file=file)
        if info.pedigree:
            print("  members:", file=file)
            for member in info.pedigree:
                print(
                    "    - { name: %s, father: %s, mother: %s, sex: %s, affected: %s }"
                    % tuple(
                        [
                            repr(x)
                            for x in (
                                member.name,
                                member.father,
                                member.mother,
                                member.sex,
                                member.affected,
                            )
                        ]
                    ),
                    file=file,
                )
        else:
            print("  members: []", file=file)
        print(file=file)
    file.flush()
