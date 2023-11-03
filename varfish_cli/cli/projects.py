"""Implementation of varfish-cli subcommand "projects *"."""

import os
import typing
import uuid

from logzero import logger
import toml
import typer

from varfish_cli import api, common
from varfish_cli.cli.common import ListObjects, RetrieveObject
from varfish_cli.common import DEFAULT_PATH_VARFISHRC, OutputFormat
from varfish_cli.config import ProjectConfig

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
    config_path: typing.Annotated[
        str,
        typer.Option("--config-path", help="Path to configuration file", envvar="VARFISH_RC_PATH"),
    ] = DEFAULT_PATH_VARFISHRC,
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

    kwargs = {"uuid": project_uuid}
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
        if setting_entry.value:
            kwargs[field_name] = field_type(setting_entry.value)
    project_config = ProjectConfig(**kwargs).model_dump(mode="json")

    logger.info("... all data retrieved, updating config...")
    logger.debug("  - project_config: %s", project_config)

    config_path = os.path.expanduser(config_path)
    if os.path.exists(config_path):
        with open(config_path, "rt") as tomlf:
            try:
                config_toml = toml.loads(tomlf.read())
            except toml.TomlDecodeError as e:
                logger.error("could not parse configuration file %s: %s", config_path, e)
                raise typer.Exit(1)
    else:
        config_toml = {}

    config_toml.setdefault("projects", [])
    match_idx = None
    for idx, project in enumerate(config_toml["projects"]):
        if project["uuid"] == str(project_config["uuid"]):
            match_idx = idx
            break
    else:
        config_toml["projects"].append(project_config)
    if match_idx is not None:
        config_toml["projects"][match_idx] = project_config

    with open(config_path, "wt") as outputf:
        outputf.write(toml.dumps(config_toml))
    logger.info("All done. Have a nice day!")
