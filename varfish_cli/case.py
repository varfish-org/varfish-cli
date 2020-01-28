"""Implementation of varfish-cli subcommand."""

import argparse
import sys
import uuid

import attr
from logzero import logger

from .common import run_nocmd, Config
from . import api


def setup_argparse(parser: argparse.ArgumentParser) -> None:
    """Main entry point for subcommand."""
    subparsers = parser.add_subparsers(dest="case_cmd")

    parser_list = subparsers.add_parser("list", help="List cases.")
    parser_list.add_argument(
        "--hidden-cmd", dest="case_cmd", default=run_list, help=argparse.SUPPRESS
    )
    parser_list.add_argument("project_uuid", help="UUID of the project to get.", type=uuid.UUID)


@attr.s(frozen=True, auto_attribs=True)
class CaseConfig:
    """Configuration for the ``varfish-cli case`` command."""

    #: Global configuration.
    global_config: Config

    @staticmethod
    def create(args, global_config, toml_config=None):
        # toml_config = toml_config or {}
        return CaseConfig(global_config=global_config)


@attr.s(frozen=True, auto_attribs=True)
class CaseListConfig:
    """Configuration for the ``varfish-cli case list`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the case to pull.
    project_uuid: uuid.UUID

    @staticmethod
    def create(args, case_config, toml_config=None):
        # toml_config = toml_config or {}
        return CaseListConfig(case_config=case_config, project_uuid=args.project_uuid)


def run_list(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run case list command."""
    config = CaseListConfig.create(args, config, toml_config)
    logger.info("Configuration: %s", config)
    logger.info("Listing cases")
    base_config = config.case_config.global_config
    res = api.case_list(
        server_url=base_config.varfish_server_url,
        api_key=base_config.varfish_api_key,
        project_uuid=config.project_uuid,
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


def run(config, toml_config, args, parser, subparser):
    """Main entry point for case command."""
    if not args.case_cmd:  # pragma: nocover
        return run_nocmd(config, args, parser, subparser)
    else:
        config = CaseConfig.create(args, config, toml_config)
        return args.case_cmd(config, toml_config, args, parser, subparser)
