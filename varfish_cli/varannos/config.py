"""Configuration classes for ``varfish-cli varannos *`` commands."""

import json
import typing
import uuid

import attr

from varfish_cli.common import CommonConfig, OutputFormat
from varfish_cli.exceptions import VarFishException


@attr.s(frozen=True, auto_attribs=True)
class VarannosConfig:
    """Configuration for the ``varfish-cli varannos`` command."""

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
        return VarannosConfig(
            output_format=OutputFormat(args.output_format),
            output_file=args.output_file,
            output_delimiter=args.output_delimiter,
            output_fields=args.output_fields.split(",") if args.output_fields else [],
            global_config=global_config,
        )


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetListConfig:
    """Configuration for the ``varfish-cli varannos varannoset-list`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the project to list the varannoset objects for.
    project_uuid: uuid.UUID

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        return VarAnnoSetListConfig(varannos_config=varannos_config, project_uuid=args.project_uuid)


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetRetrieveConfig:
    """Configuration for the ``varfish-cli varannos varannoset-retrieve`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the VarAnnoSet to retrieve.
    varannoset_uuid: uuid.UUID

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        return VarAnnoSetRetrieveConfig(
            varannos_config=varannos_config, varannoset_uuid=args.varannoset_uuid
        )


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetUpdateConfig:
    """Configuration for the ``varfish-cli varannos varannoset-update`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the VarAnnoSet to VarAnnoSetUpdateConfig.
    varannoset_uuid: uuid.UUID

    #: Field/value pairs to update.
    field_values: typing.List[typing.Tuple[str, typing.Any]]

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        field_values = []
        for field_value in args.field_values:
            try:
                key, value = field_value.split("=", 1)
                value = json.loads(value)
            except json.decoder.JSONDecodeError:
                raise VarFishException(f"Could not decode value {value} for key {key}.")
            except ValueError:
                repr_field_value = repr(field_value)
                raise VarFishException(f"Problem extracting key/value from {repr_field_value}.")
            field_values.append((key, value))
        return VarAnnoSetUpdateConfig(
            varannos_config=varannos_config,
            varannoset_uuid=args.varannoset_uuid,
            field_values=field_values,
        )


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetDestroyConfig:
    """Configuration for the ``varfish-cli varannos varannoset-destroy`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the VarAnnoSet to destroy.
    varannoset_uuid: uuid.UUID

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        return VarAnnoSetRetrieveConfig(
            varannos_config=varannos_config, varannoset_uuid=args.varannoset_uuid
        )


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetEntryListConfig:
    """Configuration for the ``varfish-cli varannos varannosetentry-list`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the VarAnnoSet to list the VarAnnoSetEntry objects for.
    varannoset_uuid: uuid.UUID

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        return VarAnnoSetEntryListConfig(
            varannos_config=varannos_config, varannoset_uuid=args.varannoset_uuid
        )


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetEntryRetrieveConfig:
    """Configuration for the ``varfish-cli varannos varannosetentry-retrieve`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the VarAnnoSetEntry to retrieve.
    varannosetentry_uuid: uuid.UUID

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        return VarAnnoSetEntryRetrieveConfig(
            varannos_config=varannos_config, varannosetentry_uuid=args.varannosetentry_uuid
        )


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetEntryUpdateConfig:
    """Configuration for the ``varfish-cli varannos varannosetentry-update`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the VarAnnoSetEntry to VarAnnoSetEntryUpdateConfig.
    varannosetentry_uuid: uuid.UUID

    #: Field/value pairs to update.
    field_values: typing.List[typing.Tuple[str, typing.Any]]

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        field_values = []
        for field_value in args.field_values:
            try:
                key, value = field_value.split("=", 1)
                value = json.loads(value)
            except json.decoder.JSONDecodeError:
                raise VarFishException(f"Could not decode value {value} for key {key}.")
            except ValueError:
                repr_field_value = repr(field_value)
                raise VarFishException(f"Problem extracting key/value from {repr_field_value}.")
            field_values.append((key, value))
        return VarAnnoSetEntryUpdateConfig(
            varannos_config=varannos_config,
            varannosetentry_uuid=args.varannosetentry_uuid,
            field_values=field_values,
        )


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetEntryDestroyConfig:
    """Configuration for the ``varfish-cli varannos varannosetentry-destroy`` command."""

    #: Case configuration.
    varannos_config: VarannosConfig

    #: UUID of the VarAnnoSetEntry to destroy.
    varannosetentry_uuid: uuid.UUID

    @staticmethod
    def create(args, varannos_config, toml_config=None):
        _ = toml_config
        return VarAnnoSetEntryRetrieveConfig(
            varannos_config=varannos_config, varannosetentry_uuid=args.varannosetentry_uuid
        )
