"""Implementation of varfish-cli subcommand 'varannos'."""

import typing
import uuid

import typer

from varfish_cli import api, common
from varfish_cli.cli.common import ListObjects, RetrieveObject
from varfish_cli.common import OutputFormat

#: Default fields for varannos.
DEFAULT_FIELDS: typing.Dict[str, typing.Optional[typing.Tuple[str]]] = {
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

#: The ``Typer`` instance to use for the ``varannos`` sub command.
app = typer.Typer(no_args_is_help=True)


@app.command("varannoset-list")
def cli_varannoset_list(
    ctx: typer.Context,
    project_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of project to list varannos for")
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

    lister = ListObjects(api.VarAnnoSetV1)
    return lister.run(
        common_options=common_options,
        callable=api.varannoset_list,
        output_file=output_file,
        output_format=output_format,
        output_delimiter=output_delimiter,
        output_fields=output_fields,
        project_uuid=project_uuid,
        default_fields=DEFAULT_FIELDS,
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

    retriever = RetrieveObject(api.Project)
    return retriever.run(
        common_options=common_options,
        callable=api.varannoset_retrieve,
        key_name="varannoset_uuid",
        object_uuid=object_uuid,
        output_file=output_file,
    )
