"""Implementation of varfish-cli subcommand "cases-import *"."""

import typing
import uuid

from logzero import logger
import typer

from varfish_cli import api, common
from varfish_cli.cli.common import ListObjects, RetrieveObject
from varfish_cli.common import DEFAULT_PATH_VARFISHRC, OutputFormat

#: The ``Typer`` instance to use for the ``cases-import`` sub command.
app = typer.Typer(no_args_is_help=True)


@app.command("bootstrap-phenopackets")
def cli_bootstrap_phenopackets(
    ctx: typer.Context,
    project_uuid: typing.Annotated[uuid.UUID, typer.Argument(..., help="UUID of project")],
    phenopacket_file: typing.Annotated[
        str, typer.Argument(..., help="Path of phenopacket file to bootstrap")
    ],
    other_files: typing.Annotated[
        typing.List[str], typer.Argument(..., help="Paths of files to incorporate")
    ],
    target_region: typing.Annotated[
        typing.List[str], typer.Option("--target-region", help="Target region specification")
    ],
    config_path: typing.Annotated[
        str,
        typer.Option("--config-path", help="Path to configuration file", envvar="VARFISH_RC_PATH"),
    ] = DEFAULT_PATH_VARFISHRC,
):
    """Bootstrap a new or existing phenopackets YAML file"""
    common_options: common.CommonOptions = ctx.obj

    #: load configuration for the selected project
    logger.info("Loading configuration for project %s from %s", project_uuid, config_path)
    project_config = common.load_project_config(project_uuid, config_path=config_path)
    if not project_config:
        logger.error("No configuration found for project %s", project_uuid)
        raise typer.Exit(1)
