"""Implementation of varfish-cli subcommand 'varannos'."""

import typing
import uuid

import typer

from varfish_cli import api, common
from varfish_cli.cli.common import ListObjects, RetrieveObject
from varfish_cli.common import OutputFormat

#: Default fields for varannos.
DEFAULT_FIELDS: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str]]] = {
    OutputFormat.TABLE: (
        "sodar_uuid",
        "date_modified",
        "project",
        "title",
        "release",
        "fields",
    ),
    OutputFormat.CSV: None,
    OutputFormat.JSON: None,
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

    lister = ListObjects(
        common_options=common_options,
        typ=api.VarAnnoSetV1,
        default_fields=DEFAULT_FIELDS,
        project_uuid=project_uuid,
        callable=api.varannoset_list,
    )
    return lister.run(
        output_file=output_file,
        output_format=output_format,
        output_delimiter=output_delimiter,
        output_fields=output_fields,
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
    common_options: common.CommonOptions = ctx.obj

    retriever = RetrieveObject(
        common_options=common_options,
        typ=api.Project,
        key_name="varannoset_uuid",
        object_uuid=object_uuid,
        callable=api.varannoset_retrieve,
    )
    return retriever.run(
        output_file=output_file,
    )
