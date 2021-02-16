"""Implementation of ``varfish-cli case list``."""

import argparse
import sys
import uuid

from logzero import logger

from .. import api
from .config import CaseListConfig


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument("project_uuid", help="UUID of the project to get.", type=uuid.UUID)


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run case list command."""
    config = CaseListConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing cases")
    base_config = config.case_config.global_config
    res = api.case_list(
        server_url=base_config.varfish_server_url,
        api_token=base_config.varfish_api_token,
        project_uuid=config.project_uuid,
        verify_ssl=config.case_config.global_config.verify_ssl,
    )

    print("Case List", file=file)
    print("=========", file=file)
    print(file=file)
    for case in res:
        print("- uuid: %s" % repr(str(case.sodar_uuid)), file=file)
        print("  name: %s" % repr(case.name), file=file)
        print("  index: %s" % repr(case.index), file=file)
        print("  members:", file=file)
        for member in case.pedigree:
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
        print()
