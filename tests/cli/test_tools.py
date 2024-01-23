"""Tests for the varfish_cli.tools module."""

from syrupy import SnapshotAssertion
from typer.testing import CliRunner

from varfish_cli.cli import app
from varfish_cli.cli.tools import load_bam_qc


def test_load_bam_qc(
    snapshot: SnapshotAssertion,
):
    samples = ["sample", "sample2"]
    cov_metrics = {
        "sample": "tests/cli/data/dragen_qc/sample.qc-coverage-region-1_coverage_metrics.csv",
        "sample2": "tests/cli/data/dragen_qc/sample2.qc-coverage-region-1_coverage_metrics.csv",
    }
    mapping_metrics = {
        "sample": "tests/cli/data/dragen_qc/sample.mapping_metrics.csv",
        "sample2": "tests/cli/data/dragen_qc/sample2.mapping_metrics.csv",
    }
    result = load_bam_qc(samples, cov_metrics, mapping_metrics)
    assert result == snapshot


def test_dragen_to_bam_qc(
    runner: CliRunner,
    snapshot: SnapshotAssertion,
    tmpdir: str,
):
    result = runner.invoke(
        app,
        [
            "--verbose",
            "tools",
            "dragen-to-bam-qc",
            f"{tmpdir}/OUT.tsv",
            "tests/cli/data/dragen_qc/sample2.mapping_metrics.csv",
            "tests/cli/data/dragen_qc/sample2.qc-coverage-region-1_coverage_metrics.csv",
            "tests/cli/data/dragen_qc/sample.mapping_metrics.csv",
            "tests/cli/data/dragen_qc/sample.qc-coverage-region-1_coverage_metrics.csv",
            "tests/cli/data/dragen_qc/samples.ped",
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output == snapshot
