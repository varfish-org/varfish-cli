"""Implementation of varfish-cli subcommand 'varannos'."""

import typing
import uuid

import pydantic
import typer

from varfish_cli import api, common
from varfish_cli.cli.common import (
    CreateObject,
    DeleteObject,
    ListObjects,
    RetrieveObject,
    UpdateObject,
)
from varfish_cli.common import OutputFormat

#: Default fields for Varannoset.
DEFAULT_FIELDS_VARANNOSET: typing.Dict[str, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE.value: (
        "sodar_uuid",
        "date_modified",
        "project",
        "title",
        "release",
        "fields",
    ),
    OutputFormat.CSV.value: None,
    OutputFormat.JSON.value: None,
}
#: Default fields for VarannosetEntry.
DEFAULT_FIELDS_VARANNOSETENTRY: typing.Dict[str, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE.value: (
        "sodar_uuid",
        "date_modified",
        "varannoset",
        "release",
        "chromosome",
        "start",
        "end",
        "reference",
        "alternative",
        "payload",
    ),
    OutputFormat.CSV.value: None,
    OutputFormat.JSON.value: None,
}

#: The ``Typer`` instance to use for the ``varannos`` sub command.
app = typer.Typer(no_args_is_help=True)


@app.command("varannoset-list")
def cli_varannoset_list(
    ctx: typer.Context,
    project_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of project to list varannosets for")
    ],
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
    output_format: typing.Annotated[
        OutputFormat, typer.Option("--output-format", help="Output format")
    ] = OutputFormat.TABLE.value,
    output_delimiter: typing.Annotated[
        str, typer.Option("--output-delimiter", help="Delimiter for CSV output")
    ] = ",",
    output_fields: typing.Annotated[
        typing.Optional[typing.List[str]], typer.Option("--output-fields", help="Output fields")
    ] = None,
):
    """List all Varannoset entries for the"""
    common_options: common.CommonOptions = ctx.obj

    list_objects = ListObjects(api.VarAnnoSetV1)
    return list_objects.run(
        common_options=common_options,
        callable=api.varannoset_list,
        output_file=output_file,
        output_format=output_format,
        output_delimiter=output_delimiter,
        output_fields=output_fields,
        parent_uuid=project_uuid,
        default_fields=DEFAULT_FIELDS_VARANNOSET,
    )


@app.command("varannoset-create")
def cli_varannoset_create(
    ctx: typer.Context,
    project_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the project to create it in")
    ],
    payload_or_path: typing.Annotated[
        str, typer.Argument(..., help="JSON with payload to use or @path with JSON")
    ] = "-",
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Create new Varannoset"""
    common_options: common.CommonOptions = ctx.obj

    payload = pydantic.TypeAdapter(api.VarAnnoSetV1).validate_python(
        common.load_json(payload_or_path)
    )

    create_object = CreateObject(api.VarAnnoSetV1)
    return create_object.run(
        common_options=common_options,
        callable=api.varannoset_create,
        parent_key_name="project_uuid",
        parent_uuid=project_uuid,
        payload=payload,
        output_file=output_file,
    )


@app.command("varannoset-retrieve")
def cli_varannoset_retrieve(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the object to retrieve")
    ],
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Retrieve Varannoset by UUID"""
    common_options: common.CommonOptions = ctx.obj

    retrieve_object = RetrieveObject(api.VarAnnoSetV1)
    return retrieve_object.run(
        common_options=common_options,
        callable=api.varannoset_retrieve,
        key_name="varannoset_uuid",
        object_uuid=object_uuid,
        output_file=output_file,
    )


@app.command("varannoset-update")
def cli_varannoset_update(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the varannoset to update")
    ],
    payload_or_path: typing.Annotated[
        str, typer.Argument(..., help="JSON with payload to use or @path with JSON")
    ] = "-",
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Create new Varannoset"""
    common_options: common.CommonOptions = ctx.obj

    payload = pydantic.TypeAdapter(api.VarAnnoSetV1).validate_python(
        common.load_json(payload_or_path)
    )

    update_object = UpdateObject(api.VarAnnoSetV1)
    return update_object.run(
        common_options=common_options,
        callable=api.varannoset_update,
        object_key_name="varannoset_uuid",
        object_uuid=object_uuid,
        payload=payload,
        output_file=output_file,
    )


@app.command("varannoset-delete")
def cli_varannoset_delete(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the varannoset to delete")
    ],
):
    """Create new Varannoset"""
    common_options: common.CommonOptions = ctx.obj

    delete_object = DeleteObject(api.VarAnnoSetV1)
    return delete_object.run(
        common_options=common_options,
        callable=api.varannoset_destroy,
        object_key_name="varannoset_uuid",
        object_uuid=object_uuid,
    )


@app.command("varannosetentry-list")
def cli_varannosetentry_list(
    ctx: typer.Context,
    varannoset_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of varannoset to list entries for")
    ],
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
    output_format: typing.Annotated[
        OutputFormat, typer.Option("--output-format", help="Output format")
    ] = OutputFormat.TABLE.value,
    output_delimiter: typing.Annotated[
        str, typer.Option("--output-delimiter", help="Delimiter for CSV output")
    ] = ",",
    output_fields: typing.Annotated[
        typing.Optional[typing.List[str]], typer.Option("--output-fields", help="Output fields")
    ] = None,
):
    """List all Varannoset entries for the"""
    common_options: common.CommonOptions = ctx.obj

    list_objects = ListObjects(api.VarAnnoSetEntryV1)
    return list_objects.run(
        common_options=common_options,
        callable=api.varannosetentry_list,
        output_file=output_file,
        output_format=output_format,
        output_delimiter=output_delimiter,
        output_fields=output_fields,
        parent_uuid=varannoset_uuid,
        parent_key="varannoset_uuid",
        default_fields=DEFAULT_FIELDS_VARANNOSETENTRY,
    )


@app.command("varannosetentry-create")
def cli_varannosetentry_create(
    ctx: typer.Context,
    varannoset_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the Varannoset to create it in")
    ],
    payload_or_path: typing.Annotated[
        str, typer.Argument(..., help="JSON with payload to use or @path with JSON")
    ] = "-",
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Create new Varannoset"""
    common_options: common.CommonOptions = ctx.obj

    payload = pydantic.TypeAdapter(api.VarAnnoSetEntryV1).validate_python(
        common.load_json(payload_or_path)
    )

    create_object = CreateObject(api.VarAnnoSetEntryV1)
    return create_object.run(
        common_options=common_options,
        callable=api.varannosetentry_create,
        parent_key_name="varannoset_uuid",
        parent_uuid=varannoset_uuid,
        payload=payload,
        output_file=output_file,
    )


@app.command("varannosetentry-retrieve")
def cli_varannosetentry_retrieve(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the object to retrieve")
    ],
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Retrieve VarannosetEntry by UUID"""
    common_options: common.CommonOptions = ctx.obj

    retrieve_object = RetrieveObject(api.VarAnnoSetEntryV1)
    return retrieve_object.run(
        common_options=common_options,
        callable=api.varannosetentry_retrieve,
        key_name="varannosetentry_uuid",
        object_uuid=object_uuid,
        output_file=output_file,
    )


@app.command("varannosetentry-update")
def cli_varannosetentry_update(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the varannosetentry to update")
    ],
    payload_or_path: typing.Annotated[
        str, typer.Argument(..., help="JSON with payload to use or @path with JSON")
    ] = "-",
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Create new Varannoset"""
    common_options: common.CommonOptions = ctx.obj

    payload = pydantic.TypeAdapter(api.VarAnnoSetEntryV1).validate_python(
        common.load_json(payload_or_path)
    )

    update_object = UpdateObject(api.VarAnnoSetEntryV1)
    return update_object.run(
        common_options=common_options,
        callable=api.varannosetentry_update,
        object_key_name="varannosetentry_uuid",
        object_uuid=object_uuid,
        payload=payload,
        output_file=output_file,
    )


@app.command("varannosetentry-delete")
def cli_varannosetentry_delete(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the varannosetentry to delete")
    ],
):
    """Create new varannosetentry"""
    common_options: common.CommonOptions = ctx.obj

    delete_object = DeleteObject(api.VarAnnoSetEntryV1)
    return delete_object.run(
        common_options=common_options,
        callable=api.varannosetentry_destroy,
        object_key_name="varannosetentry_uuid",
        object_uuid=object_uuid,
    )
