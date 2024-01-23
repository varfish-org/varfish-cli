"""Implementation of varfish-cli subcommand "tools *"."""

import csv
import fnmatch
import gzip
from typing import Annotated, Dict, List

from logzero import logger
import typer

from varfish_cli.cli.tools.models import BamQc, BamQcData
from varfish_cli.config import CommonOptions
from varfish_cli.parse_ped import parse_ped

#: The ``Typer`` instance to use for the ``tools`` sub command.
app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


def load_sample_data(qc_coverage_region_path: str, mapping_metrics_path: str) -> BamQcData:
    """Load data for one sample from DRAGEN QC files.

    :param qc_coverage: Path to QC coverage file
    :param mapping_metrics: Path to coverage metrics file
    :raises typer.Exit: If there is a problem with reading the input files.
    """
    fieldnames = ["_coverage_summary", "_empty", "label", "value"]
    qc_coverage_region: Dict[str, str] = {}
    with open(qc_coverage_region_path, "rt") as qc_coverage_file:
        reader = csv.DictReader(
            qc_coverage_file,
            fieldnames=fieldnames,
            delimiter=",",
        )
        qc_coverage_region = {row["label"]: row["value"] for row in reader}
    mapping_metrics: Dict[str, str] = {}
    with open(mapping_metrics_path, "rt") as coverage_metrics_file:
        reader = csv.DictReader(coverage_metrics_file, fieldnames=fieldnames, delimiter=",")
        mapping_metrics = {row["label"]: row["value"] for row in reader}

    key_aligned_in_region = "Aligned bases in QC coverage region"
    try:
        aligned_bases_in_region = int(qc_coverage_region[key_aligned_in_region])
    except (KeyError, ValueError) as e:
        logger.error(f"'{key_aligned_in_region}' not in {qc_coverage_region_path} or no int")
        raise typer.Exit() from e
    key_avg_cov_in_region = "Average alignment coverage over QC coverage region"
    try:
        avg_cov_in_region = float(qc_coverage_region[key_avg_cov_in_region])
    except (KeyError, ValueError) as e:
        logger.error(f"'{key_avg_cov_in_region}' not in {qc_coverage_region_path} or no float")
        raise typer.Exit() from e

    key_pct = "PCT of QC coverage region with coverage"
    min_cov_target: Dict[int, float] = {}
    min_cov_keys = list(
        reversed([k for k in qc_coverage_region.keys() if k.startswith(key_pct) and ": inf" in k])
    )
    for key in min_cov_keys:
        min_cov = int(key[len(key_pct) + 2 :].split(":")[0][:-1].strip())
        try:
            min_cov_target[min_cov] = float(qc_coverage_region[key])
        except (KeyError, ValueError) as e:
            logger.error(f"'{key}' not in {qc_coverage_region_path} or no float")
            raise typer.Exit() from e

    key_total_input_reads = "Total input reads"
    try:
        total_input_reads = int(mapping_metrics[key_total_input_reads])
    except (KeyError, ValueError) as e:
        logger.error(f"'{key_total_input_reads}' not in {mapping_metrics_path} or no int")
        raise typer.Exit() from e
    key_duplicate_reads = "Number of duplicate marked reads"
    try:
        duplicate_reads = int(mapping_metrics[key_duplicate_reads])
    except (KeyError, ValueError) as e:
        logger.error(f"'{key_duplicate_reads}' not in {mapping_metrics_path} or no int")
        raise typer.Exit() from e
    key_insert_length_mean = "Insert length: mean"
    try:
        insert_length_mean = float(mapping_metrics[key_insert_length_mean])
    except (KeyError, ValueError) as e:
        logger.error(f"'{key_insert_length_mean}' not in {mapping_metrics_path} or no int")
        raise typer.Exit() from e
    key_insert_length_std = "Insert length: standard deviation"
    try:
        insert_length_std = float(mapping_metrics[key_insert_length_std])
    except (KeyError, ValueError) as e:
        logger.error(f"'{key_insert_length_std}' not in {mapping_metrics_path} or no int")
        raise typer.Exit() from e

    return BamQcData(
        summary={
            "mean coverage": avg_cov_in_region,
            "total target size": int(aligned_bases_in_region / avg_cov_in_region),
        },
        min_cov_target=min_cov_target,
        bamstats={
            "sequences": total_input_reads,
            "reads duplicated": duplicate_reads,
            "insert size average": insert_length_mean,
            "insert size standard deviation": insert_length_std,
        },
    )


def load_bam_qc(
    samples: List[str],
    sample_qc_coverage_region: Dict[str, str],
    mapping_metrics: Dict[str, str],
) -> BamQc:
    """Load the BAM QC data

    :param samples: List of sample names
    :param sample_qc_coverage: Mapping from sample name to QC coverage file name
    :param mapping_metrics: Mapping from sample name to mapping metrics file name
    :return: ``BamQc`` object
    """
    return BamQc(
        sample_data={
            sample: load_sample_data(sample_qc_coverage_region[sample], mapping_metrics[sample])
            for sample in samples
        }
    )


@app.command("dragen-to-bam-qc")
def dragen_to_bam_qc(
    ctx: typer.Context,
    output_file: Annotated[str, typer.Argument(..., help="Path to 'legacy' varfish BAM QC")],
    input_files: Annotated[
        List[str],
        typer.Argument(
            ...,
            help="Path to DRAGEN QC files (*.ped, *.qc-coverage*.csv and *.mapping_metrics.csv)",
        ),
    ],
):
    """Convert DRAGEN QC files to legacy 'bam-qc' format.

    :param ctx: Typer Context
    :param output_file: Path to output file
    :param input_files: List of input files
    :raise typer.Exit: If input files are not found
    """
    common_options: CommonOptions = ctx.obj
    _ = common_options
    logger.info("Converting DRAGEN QC information")

    # Check that output path ends in .tsv or .tsv.gz.
    if not output_file.endswith((".tsv", ".tsv.gz")):
        logger.error("Output file must end in .tsv or .tsv.gz")
        raise typer.Exit()

    # Look for exactly one PED file and read it.
    logger.info("Looking for PED file ...")
    ped_file = None
    for input_file in input_files:
        if ped_file and input_file.endswith((".ped", ".ped.gz")):
            logger.error("Found more than one PED file.")
            raise typer.Exit()
        if input_file.endswith(".ped"):
            logger.info(f"... found PED file: {input_file}")
            ped_file = open(input_file, "rt")
        elif input_file.endswith(".ped.gz"):
            logger.info(f"... found PED.gz file: {input_file}")
            ped_file = gzip.open(input_file, "rt")
    if not ped_file:
        logger.error("No PED file found (looked for *.ped, *.ped.gz)")
        raise typer.Exit()

    logger.info("... PED is: \n{}")
    with ped_file:
        donors = parse_ped(ped_file)
    samples = [donor.name for donor in donors]
    logger.info(f"... donors: {donors}")

    logger.info("Looking for QC files ...")
    # Check that input paths contains one `*.qc-coverage-*` and one `*.mapping_metrics.csv`
    # file per sample:
    sample_qc_coverage = {}
    mapping_metrics = {}
    for sample in samples:
        pat_qc_coverage = f"*/{sample}.qc-coverage-*.csv"
        pat_mapping_metric = f"*/{sample}.mapping_metrics.csv"
        cand_qc_coverage = fnmatch.filter(input_files, pat_qc_coverage)
        if cand_qc_coverage:
            sample_qc_coverage[sample] = cand_qc_coverage[0]
            logger.info(f"  {sample} => {cand_qc_coverage[0]}")
        else:
            logger.error(f"  {sample} => no match for {pat_qc_coverage}")
        cand_mapping_metrics = fnmatch.filter(input_files, pat_mapping_metric)
        if cand_mapping_metrics:
            mapping_metrics[sample] = cand_mapping_metrics[0]
            logger.info(f"  {sample} => {cand_mapping_metrics[0]}")
        else:
            logger.error(f"  {sample} => no match for {mapping_metrics}")
    if len(sample_qc_coverage) != len(samples) or len(mapping_metrics) != len(samples):
        logger.error("Not all samples have QC files (see above)")
        raise typer.Exit()
    else:
        logger.info("... all samples have QC files")

    # Load data and create ``BamQc`` object.
    print(samples, sample_qc_coverage, mapping_metrics)
    bam_qc: BamQc = load_bam_qc(samples, sample_qc_coverage, mapping_metrics)

    # Write result.
    logger.debug(f"Opening output file {output_file} ...")
    if output_file.endswith(".tsv.gz"):
        output_file = gzip.open(output_file, "wt")
    else:
        output_file = open(output_file, "wt")
    with output_file:
        json_str = bam_qc.model_dump_json().replace('"', '"""')
        print(f"case_id\tset_id\tbam_stats\n.\t.\t{json_str}", file=output_file)
    logger.debug("... done writing output file.")

    logger.info("All done. Have a nice day! 😊")
