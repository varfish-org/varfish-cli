"""Configuration classes for ``varfish-cli case *`` commands."""

import attr
import uuid

from ..common import CommonConfig


@attr.s(frozen=True, auto_attribs=True)
class CaseConfig:
    """Configuration for the ``varfish-cli case`` command."""

    #: Global configuration.
    global_config: CommonConfig

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
