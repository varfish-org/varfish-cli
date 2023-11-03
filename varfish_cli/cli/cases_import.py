"""Implementation of varfish-cli subcommand "cases-import *"."""

import datetime
import os
import typing
import uuid

from google.protobuf.json_format import MessageToDict, ParseDict, ParseError
from logzero import logger
from phenopackets import Family
import typer
import yaml

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
    # load configuration for the selected project
    logger.info("Loading configuration for project %s from %s", project_uuid, config_path)
    project_config = common.load_project_config(project_uuid, config_path=config_path)
    if not project_config:
        logger.error("No configuration found for project %s", project_uuid)
        raise typer.Exit(1)

    # split files by file type
    assert False

    # if we do not have a phenopacket file, ensure that we have a PED file
    assert False

    # load phenopacket file or create new one
    family: Family
    create_output: bool
    if os.path.exists(phenopacket_file):
        create_output = False
        with open(phenopacket_file, "rt") as inputf:
            try:
                yaml_dict = yaml.safe_load(inputf)
            except yaml.parser.ParserError as e:
                logger.error("Could not parse phenopacket YAML file: %s", e)
                raise typer.Exit(1)
        if "family" not in yaml_dict:  # pragma: no cover
            logger.error("No 'family' section found at top of phenopacket YAML file")
            raise typer.Exit(1)
        try:
            family = ParseDict(js_dict=yaml_dict["family"], message=Family())
        except ParseError as e:  # pragma: no cover
            logger.error("Could not load phenopacket data: %s", e)
            raise typer.Exit(1)
    else:
        create_output = True
        family = Family()

    # sync members in PED and phenopackets file
    assert False

    # write out phenopackets file
    if create_output:
        logger.info("Creating new phenopacket file %s", phenopacket_file)
    else:
        timestamp = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        path_bak = f"{phenopacket_file}.bak~{timestamp}"
        logger.info("Move file %s => %s", phenopacket_file, path_bak)
        os.rename(phenopacket_file, path_bak)
        logger.info("Re-creating phenopacket file %s", phenopacket_file)
    with open(phenopacket_file, "wt") as outputf:
        yaml.dump({"family": MessageToDict(family)}, outputf)

    logger.info("All done. Have a nice day!")
