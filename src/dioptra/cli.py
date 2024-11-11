from pathlib import Path

import click

from dioptra.context.calibrate import calibrate_main
from dioptra.context.list import list_main
from dioptra.estimate.annotate import annotate_main
from dioptra.estimate.render import render_main
from dioptra.estimate.report import report_main


@click.group()
def cli() -> None:
    """The Dioptra FHE platform."""
    pass


@cli.group()
def estimate() -> None:
    """Estimate properties of an OpenFHE program."""
    pass


@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--calibration-data",
    "-cd",
    type=click.Path(exists=True),
    required=True,
    help="File containing calibration data to use for the estimate.",
)
def report(file: Path, calibration_data: Path) -> None:
    """Estimate FHE runtime and memory usage for decorated functions.

    FILE is the python file to look for functions decorated with
    "@dioptra_estimation" or "@dioptra_binfhe_estimation".
    """
    report_main(str(calibration_data), [str(file)])


@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--calibration-data",
    "-cd",
    type=click.Path(exists=True),
    required=True,
    help="File containing calibration data to use for the estimate.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    required=True,
    help="Output directory for annotated files.",
)
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Name of the estimation case to annotate.",
)
def annotate(file: Path, calibration_data: Path, name: str, output: Path) -> None:
    """Annotate Python source files with estimated FHE runtimes.

    FILE is the python file to look for functions decorated with
    "@dioptra_estimation" or "@dioptra_binfhe_estimation".
    """
    annotate_main(str(calibration_data), str(file), name, str(output))


@cli.group()
def context() -> None:
    """Generate FHE runtime/memory calibration data."""
    pass


@context.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Name of the context function to generate data for.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    required=True,
    help="File to output calibration data to.",
)
@click.option(
    "--sample-count",
    "-sc",
    type=int,
    default=5,
    help="Number of samples to take (default: 5).",
)
def calibrate(file: Path, name: str, output: Path, sample_count: int):
    """Run calibration for a decorated context function.

    FILE is the python file to look for functions decorated with
    "@dioptra_context" or "@dioptra_binfhe_context".
    """
    calibrate_main([str(file)], name, str(output), sample_count)


@context.command()
@click.argument("file", type=click.Path(exists=True), required=True)
def list(file: Path):
    """List decorated context functions.

    FILE is the python file to look for functions decorated with
    "@dioptra_context" or "@dioptra_binfhe_context".
    """
    list_main([str(file)])


@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--calibration-data",
    "-cd",
    type=click.Path(exists=True),
    required=True,
    help="File containing calibration data to use for the estimate.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    help="Output directory for render results.",
)
def render(file: Path, calibration_data: Path, output: Path) -> None:
    """Run decorated functions and render analysis results."""
    render_main(str(calibration_data), str(file), str(output))
