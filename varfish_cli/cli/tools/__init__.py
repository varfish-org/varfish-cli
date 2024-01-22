"""Implementation of varfish-cli subcommand "tools *"."""

import typing

from logzero import logger
import typer

from varfish_cli.config import CommonOptions

#: The ``Typer`` instance to use for the ``tools`` sub command.
app = typer.Typer(no_args_is_help=True)


@app.command("convert-dragen-bam-qc")
def run(
    ctx: typer.Context,
    output_file: typing.Annotated[str, typer.Argument(..., help="Path to 'legacy' varfish BAM QC")],
    input_files: typing.Annotated[
        typing.List[str],
        typer.Argument(
            ..., help="Path to DRAGEN QC files (*.ped, *.qc-coverage*.csv and *.mapping_metrics.csv)"
        ),
    ],
):
    """Convert DRAGEN QC files to legacy 'bam-qc' format."""
    common_options: CommonOptions = ctx.obj
    logger.info("Converting DRAGEN QC information")
    # check that output path ends in .tsv or .tsv.gz
    # check that input paths contain exactly one PED file
    # check that input paths contains one `*.qc-coverage-*` file per sample
    # check that input paths contains one `*.mapping_metrics.csv` file per sample
