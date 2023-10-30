"""Implementation of varfish-cli subcommand 'projects'."""

import typing
import uuid

import typer

from varfish_cli import api, common
from varfish_cli.cli.common import ListObjects, RetrieveObject
from varfish_cli.common import OutputFormat

#: Default fields for projects.
DEFAULT_FIELDS: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str, ...]]] = {
    OutputFormat.TABLE.value: (
        "sodar_uuid",
        "type",
        "title",
    ),
    OutputFormat.CSV.value: None,
    OutputFormat.JSON.value: None,
}

#: The ``Typer`` instance to use for the ``projects`` sub command.
app = typer.Typer(no_args_is_help=True)


@app.command("project-list")
def cli_list(
    ctx: typer.Context,
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
    """List all projects"""
    common_options: common.CommonOptions = ctx.obj

    lister = ListObjects(
        common_options=common_options,
        typ=api.Project,
        default_fields=DEFAULT_FIELDS,
        callable=api.project_list,
    )
    return lister.run(
        output_file=output_file,
        output_format=output_format,
        output_delimiter=output_delimiter,
        output_fields=output_fields,
    )


@app.command("project-retrieve")
def cli_retrieve(
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
        key_name="project_uuid",
        object_uuid=object_uuid,
        callable=api.project_retrieve,
    )
    return retriever.run(
        output_file=output_file,
    )
