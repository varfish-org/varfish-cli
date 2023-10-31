"""Implementation of varfish-cli subcommand "cases *"."""

import typing
import uuid

import typer

from varfish_cli import api, common
from varfish_cli.cli.common import ListObjects, RetrieveObject
from varfish_cli.common import OutputFormat

#: Default fields for projects.
DEFAULT_FIELDS_CASE: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str, ...]]] = {
    OutputFormat.TABLE.value: ("sodar_uuid", "name", "index", "members"),
    OutputFormat.CSV.value: None,
    OutputFormat.JSON.value: None,
}

#: The ``Typer`` instance to use for the ``cases`` sub command.
app = typer.Typer(no_args_is_help=True)


@app.command("case-list")
def cli_case_list(
    ctx: typer.Context,
    project_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of project to list cases for")
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
    """List all Case entries for the"""
    common_options: common.CommonOptions = ctx.obj

    list_objects = ListObjects(api.Case)
    return list_objects.run(
        common_options=common_options,
        callable=api.case_list,
        output_file=output_file,
        output_format=output_format,
        output_delimiter=output_delimiter,
        output_fields=output_fields,
        parent_uuid=project_uuid,
        default_fields=DEFAULT_FIELDS_CASE,
    )


@app.command("case-retrieve")
def cli_case_retrieve(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the object to retrieve")
    ],
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Retrieve Case by UUID"""
    common_options: common.CommonOptions = ctx.obj

    retrieve_object = RetrieveObject(api.Case)
    return retrieve_object.run(
        common_options=common_options,
        callable=api.case_retrieve,
        key_name="case_uuid",
        object_uuid=object_uuid,
        output_file=output_file,
    )
