"""Implementation of varfish-cli subcommand "projects *"."""

import typing
import uuid

from logzero import logger
import typer

from varfish_cli import api, common
from varfish_cli.cli.common import ListObjects, RetrieveObject
from varfish_cli.common import OutputFormat
from varfish_cli.config import CommonOptions

#: Default fields for projects.
DEFAULT_FIELDS_PROJECT: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str, ...]]] = {
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
def cli_project_list(
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

    lister = ListObjects(api.Project)
    return lister.run(
        common_options=common_options,
        callable=api.project_list,
        output_file=output_file,
        output_format=output_format,
        output_delimiter=output_delimiter,
        output_fields=output_fields,
        default_fields=DEFAULT_FIELDS_PROJECT,
    )


@app.command("project-retrieve")
def cli_project_retrieve(
    ctx: typer.Context,
    object_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the object to retrieve")
    ],
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Retrieve project by UUID"""
    common_options: common.CommonOptions = ctx.obj

    retriever = RetrieveObject(api.Project)
    return retriever.run(
        common_options=common_options,
        callable=api.project_retrieve,
        key_name="project_uuid",
        object_uuid=object_uuid,
        output_file=output_file,
    )


@app.command("project-load-config")
def cli_project_load_config(
    ctx: typer.Context,
    project_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of the object to retrieve")
    ],
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    """Load project configuration for import and store in ~/.varfishrc.toml"""
    common_options: common.CommonOptions = ctx.obj
    logger.info("Retrieving project configuration...")

    fields_types = {
        "import_data_host": str,
        "import_data_password": str,
        "import_data_path": str,
        "import_data_port": int,
        "import_data_protocol": str,
        "import_data_user": str,
    }

    kwargs = {}
    for field_name, field_type in fields_types.items():
        logger.debug(" - retrieving %s", field_name)
        setting_entry = api.project_settings_retrieve(
            server_url=common_options.varfish_server_url,
            api_token=common_options.varfish_api_token.get_secret_value(),
            project_uuid=project_uuid,
            app_name="cases_import",
            setting_name=field_name,
            verify_ssl=common_options.verify_ssl,
        )
        print(setting_entry)
        if setting_entry.value:
            kwargs[field_name] = field_type(setting_entry.value)
        print(kwargs)

    logger.info("... all data retrieved, updating config...")

    print(kwargs)
