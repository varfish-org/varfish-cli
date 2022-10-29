"""Configuration classes for ``varfish-cli case *`` commands."""

import json
import typing
import uuid

import attr

from varfish_cli.api import CONVERTER, models
from varfish_cli.common import CommonConfig, OutputFormat


@attr.s(frozen=True, auto_attribs=True)
class CaseConfig:
    """Configuration for the ``varfish-cli case`` command."""

    #: Global configuration
    global_config: CommonConfig

    #: Path to output file
    output_file: str = "-"

    #: Output format
    output_format: OutputFormat = OutputFormat.TABLE

    #: delimiter for CSV output
    output_delimiter: str = ","

    #: Fields to use for output.
    output_fields: typing.Optional[typing.List[str]] = []

    @staticmethod
    def create(args, global_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseConfig(
            output_format=OutputFormat(args.output_format),
            output_file=args.output_file,
            output_delimiter=args.output_delimiter,
            output_fields=args.output_fields.split(",") if args.output_fields else [],
            global_config=global_config,
        )


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


@attr.s(frozen=True, auto_attribs=True)
class CaseSmallVariantQueryListConfig:
    """Configuration for the ``varfish-cli case small-var-query-list`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the case to list for.
    case_uuid: uuid.UUID

    @staticmethod
    def create(args, case_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseSmallVariantQueryListConfig(case_config=case_config, case_uuid=args.case_uuid)


@attr.s(frozen=True, auto_attribs=True)
class CaseSmallVariantQueryCreateConfig:
    """Configuration for the ``varfish-cli case small-var-query-create`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the small variant query to retrieve.
    case_uuid: uuid.UUID

    #: The query settings to set.
    query_settings: models.CaseQuerySettingsV1

    #: The name of the query to set, if any.
    name: typing.Optional[str] = None

    #: Whether or not to make the query public, if any.
    public: bool = False

    @staticmethod
    def create(args, case_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        if args.query_settings.startswith("@"):
            with open(args.query_settings[1:], "rt") as inputf:
                query_settings = json.load(inputf)
        else:
            query_settings = json.loads(args.args.query_settings.startswith)
        # Allow both reading raw query_settings and response from query settings shortcuts
        if "query_settings" in query_settings:
            query_settings = query_settings["query_settings"]
        return CaseSmallVariantQueryCreateConfig(
            case_config=case_config,
            case_uuid=args.case_uuid,
            query_settings=CONVERTER.structure(query_settings, models.CaseQuerySettingsV1),
            name=args.name,
            public=args.public,
        )


@attr.s(frozen=True, auto_attribs=True)
class CaseSmallVariantQueryShortcut:
    """Configuration for the ``varfish-cli case small-var-query-shortcut`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the small variant query to retrieve.
    case_uuid: uuid.UUID

    #: The database to use
    database: str

    #: The quick preset to use
    quick_preset: str

    #: Setting in category inheritance
    inheritance: typing.Optional[str] = None

    #: Setting in category frequency
    frequency: typing.Optional[str] = None

    #: Setting in category impact
    impact: typing.Optional[str] = None

    #: Setting in category quality
    quality: typing.Optional[str] = None

    #: Setting in category chromosomes
    chromosomes: typing.Optional[str] = None

    #: Setting in category flags_etc
    flags_etc: typing.Optional[str] = None

    @staticmethod
    def create(args, case_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseSmallVariantQueryShortcut(
            case_config=case_config,
            case_uuid=args.case_uuid,
            database=args.database,
            quick_preset=args.quick_preset,
            inheritance=args.inheritance,
            frequency=args.frequency,
            impact=args.impact,
            quality=args.quality,
            chromosomes=args.chromosomes,
            flags_etc=args.flags_etc,
        )


@attr.s(frozen=True, auto_attribs=True)
class CaseSmallVariantQueryRetrieveConfig:
    """Configuration for the ``varfish-cli case small-var-query-retrieve`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the small variant query to retrieve.
    query_uuid: uuid.UUID

    @staticmethod
    def create(args, case_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseSmallVariantQueryRetrieveConfig(
            case_config=case_config, query_uuid=args.query_uuid
        )


@attr.s(frozen=True, auto_attribs=True)
class CaseSmallVariantQueryStatusConfig:
    """Configuration for the ``varfish-cli case small-var-query-status`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the small variant query to retrieve.
    query_uuid: uuid.UUID

    @staticmethod
    def create(args, case_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseSmallVariantQueryStatusConfig(
            case_config=case_config, query_uuid=args.query_uuid
        )


@attr.s(frozen=True, auto_attribs=True)
class CaseSmallVariantQueryUpdateConfig:
    """Configuration for the ``varfish-cli case small-var-query-update`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the small variant query to retrieve.
    query_uuid: uuid.UUID

    #: The name of the query to set, if any.
    name: typing.Optional[str] = None

    #: Whether or not to make the query public, if any.
    public: typing.Optional[bool] = None

    @staticmethod
    def create(args, case_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseSmallVariantQueryUpdateConfig(
            case_config=case_config, query_uuid=args.query_uuid, name=args.name, public=args.public
        )


@attr.s(frozen=True, auto_attribs=True)
class CaseSmallVariantQueryFetchResultsConfig:
    """Configuration for the ``varfish-cli case small-var-query-fetch-results`` command."""

    #: Case configuration.
    case_config: CaseConfig

    #: UUID of the small variant query to retrieve.
    query_uuid: uuid.UUID

    @staticmethod
    def create(args, case_config, toml_config=None):
        _ = toml_config
        # toml_config = toml_config or {}
        return CaseSmallVariantQueryFetchResultsConfig(
            case_config=case_config, query_uuid=args.query_uuid
        )
