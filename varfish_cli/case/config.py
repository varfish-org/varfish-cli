"""Configuration classes for ``varfish-cli case *`` commands."""

import attr
import uuid

import typing

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
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseListConfig(case_config=case_config, project_uuid=args.project_uuid)


@attr.s(frozen=True, auto_attribs=True)
class CaseListImportInfoConfig:
    """Configuration for the ``varfish-cli case list-import-info`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the case to pull.
    project_uuid: uuid.UUID

    #: Optionally, owner to query for.
    owner: typing.Optional[str] = None

    @staticmethod
    def create(args, case_config, toml_config=None):
        # toml_config = toml_config or {}
        return CaseListImportInfoConfig(
            case_config=case_config, project_uuid=args.project_uuid, owner=args.owner
        )


@attr.s(frozen=True, auto_attribs=True)
class CaseCreateImportInfoConfig:
    """Configuration for the ``varfish-cli case create-import-info`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: Suffix to append to the case name.
    case_name_suffix: str

    #: UUID of the case to pull.
    project_uuid: uuid.UUID

    #: Path to files to import.
    paths: typing.List[str]

    #: Regular expression to use for modifying family.
    strip_family_regex: str

    #: Whether to force resubmittal of old
    resubmit: bool

    #: Whether to force creation of fresh case import info.
    force_fresh: bool

    #: Expected genome build.
    genomebuild: str

    @staticmethod
    def create(args, case_config, strip_family_regex, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseCreateImportInfoConfig(
            case_config=case_config,
            project_uuid=args.project_uuid,
            paths=args.paths,
            strip_family_regex=args.strip_family_regex,
            case_name_suffix=args.case_name_suffix,
            resubmit=args.resubmit,
            force_fresh=args.force_fresh,
            genomebuild=args.genomebuild,
        )
