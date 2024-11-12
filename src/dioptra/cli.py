"""Dioptra CLI entrypoints.

Definitions of the click-decorated functions that implement the Dioptra CLI.

If you are a library author looking to build on / programmatically use the
Dioptra CLI functionalities, see the dioptra.estimate and dioptra.context
packages.
"""

from pathlib import Path

import click

from dioptra.context.calibrate import calibrate_main
from dioptra.context.list import list_main
from dioptra.estimate.annotate import annotate_main
from dioptra.estimate.render import render_main
from dioptra.estimate.report import report_main


@click.group()
def cli() -> None:
    """Dioptra: Analysis of OpenFHE applications.

    Dioptra is a library and command-line application for the analysis of Python
    programs that use OpenFHE, providing tools for calibration (to produce
    system-accurate estimates) and estimation (a "test runner" that looks for
    specially-decorated functions in Python modules).
    """
    pass


@cli.group()
def estimate() -> None:
    """Estimate runtime and memory performance of OpenFHE applications.

    All of the dioptra estimate commands assume access to calibration data, and
    modules containing appropriately-decorated estimation cases.
    """
    pass


@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--calibration-data",
    "-cd",
    type=click.Path(exists=True),
    required=True,
    help="Calibration data file to use for estimates.",
)
def report(file: Path, calibration_data: Path) -> None:
    """Report runtime and memory performance estimates for all estimation cases.

    FILE is the Python file in which to look for estimation cases (functions
    decorated with "@dioptra_estimation()" or "@dioptra_binfhe_estimation()").
    """
    report_main(str(calibration_data), [str(file)])


@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--calibration-data",
    "-cd",
    type=click.Path(exists=True),
    required=True,
    help="Calibration data file to use for estimates.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    required=True,
    help="Directory to which annotated files should be written.",
)
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Name of the estimation case to annotate.",
)
def annotate(file: Path, calibration_data: Path, name: str, output: Path) -> None:
    """Annotate Python source files with estimated OpenFHE operation runtimes.

    FILE is the Python file in which to look for estimation cases (functions
    decorated with "@dioptra_estimation()" or "@dioptra_binfhe_estimation()").
    """
    annotate_main(str(calibration_data), str(file), name, str(output))


@cli.group()
def context() -> None:
    """Generate runtime and memory calibration data for OpenFHE applications.

    To not make assumptions about your system, Dioptra estimates performance
    based on calibration data specific to your context. Dioptra's context
    commands assume access to Python modules defining specific OpenFHE contexts,
    which are particular selections of FHE schemes/parameters.
    """
    pass


@context.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Name of the context function to use to generate calibration data.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    required=True,
    help="File to which calibration data should be written.",
)
@click.option(
    "--sample-count",
    "-sc",
    type=int,
    default=5,
    help="Number of samples to take (default: 5).",
)
def calibrate(file: Path, name: str, output: Path, sample_count: int):
    """Generate calibration data for a decorated context function.

    FILE is the Python file in which to look for contexts (functions decorated
    with "@dioptra_context()" or "@dioptra_binfhe_context()".)
    """
    calibrate_main([str(file)], name, str(output), sample_count)


@context.command()
@click.argument("file", type=click.Path(exists=True), required=True)
def list(file: Path):
    """List context functions.

    FILE is the python file in which to look for contexts (functions decorated
    with "@dioptra_context()" or "@dioptra_binfhe_context()".)
    """
    list_main([str(file)])


@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--calibration-data",
    "-cd",
    type=click.Path(exists=True),
    required=True,
    help="Calibration data file to use for estimates.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=Path),
    help="Directory to which the rendered website should be written.",
)
def render(file: Path, calibration_data: Path, output: Path) -> None:
    """Render a website for an estimation case.

    FILE is the Python file in which to look for estimation cases (functions
    decorated with "@diotpra_estimation()" or "@dioptra_binfhe_estimation()").
    """
    render_main(str(calibration_data), str(file), str(output))
