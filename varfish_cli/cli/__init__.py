"""Code for main entry point."""

import logging
import typing

import typer
import logzero
from logzero import logger

from varfish_cli import __version__
from varfish_cli.cli import projects, varannos
from varfish_cli.config import CommonOptions, load_config

#: Paths to search the global configuration in.
DEFAULT_PATH_VARFISHRC = "~/.varfishrc.toml"


def version_callback(value: bool):
    """Callback when called with 'version' or '--version'"""
    if value:
        print(f"varfish-cli {__version__}")
        raise typer.Exit()


#: Main CLI ``Typer`` object.
app = typer.Typer(no_args_is_help=True)

# Register all sub commands.
app.add_typer(varannos.app, name="varannos", help="Varannos-related subcommands")
app.add_typer(projects.app, name="projects", help="Project-related subcommands")


@app.command("version")
def main_version():
    """Print version as "varfish-cli $version"."""
    version_callback(True)


@app.callback()
def main(
    ctx: typer.Context,
    version: typing.Annotated[
        typing.Optional[bool], typer.Option("--version", callback=version_callback)
    ] = None,
    verbose: typing.Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose output")
    ] = False,
    verify_ssl: typing.Annotated[
        bool, typer.Option("--verify-ssl/--no-verify-ssl", help="Disable SSL verification")
    ] = True,
    config_path: typing.Annotated[
        str,
        typer.Option("--config-path", help="Path to configuration file", envvar="VARFISH_RC_PATH"),
    ] = DEFAULT_PATH_VARFISHRC,
    varfish_server_url: typing.Annotated[
        typing.Optional[str],
        typer.Option(
            "--varfish-server-url",
            help=(
                "VarFish server URL key to use, defaults to env VARFISH_SERVER_URL or read "
                "from configfile"
            ),
            envvar="VARFISH_SERVER_URL",
        ),
    ] = None,
    varfish_api_token: typing.Annotated[
        typing.Optional[str],
        typer.Option(
            "--varfish-server-url",
            help=(
                "VarFish API token to use, defaults to env VARFISH_API_TOKEN or read from "
                "configfile"
            ),
            envvar="VARFISH_API_TOKEN",
        ),
    ] = None,
):
    """Callback for main entry point

    This function handles the global configuration from configuration file,
    environment variables, and command line (in increasing priority).
    """
    _ = version
    # Setup logging
    if verbose:  # pragma: no cover
        level = logging.DEBUG
    else:
        # Remove module name and line number if not running in debug mode.s
        formatter = logzero.LogFormatter(
            fmt="%(color)s[%(levelname)1.1s %(asctime)s]%(end_color)s %(message)s"
        )
        logzero.formatter(formatter)
        level = logging.INFO
    logzero.loglevel(level=level)

    # Load configuration file
    toml_varfish_server_url, toml_varfish_api_token = load_config(config_path)
    if toml_varfish_server_url and not varfish_server_url:
        varfish_server_url = toml_varfish_server_url
    if toml_varfish_api_token and not varfish_api_token:
        varfish_api_token = toml_varfish_api_token

    # Construct common options
    ctx.obj = CommonOptions(
        verbose=verbose,
        verify_ssl=verify_ssl,
        config_path=config_path,
        varfish_server_url=varfish_server_url,
        varfish_api_token=varfish_api_token,
    )
    logger.info("global configuration = %s", ctx.obj.model_dump_json())


#: Define ``typer`` object that can be called from ``__main__.py``.
typer_click_object = typer.main.get_command(app)
