import click
import click_log

import logging
from pathlib import Path

from dioptra import decorator
from dioptra.analyzer import calibration


logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.group()
@click_log.simple_verbosity_option(logger)
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
    "--cd",
    type=click.Path(exists=True),
    required=True,
    help="File containing calibration data to use for the estimate.",
)
def report(file: Path, cd: Path) -> None:
    """Estimate FHE runtime and memory usage for decorated functions.

    FILE is the python file to look for functions decorated with
    "@dioptra_runtime" or "@dioptra_binfhe_runtime".
    """
    decorator.report_main(str(cd), [str(file)])


@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--cd",
    type=click.Path(exists=True),
    required=True,
    help="File containing calibration data to use for the estimate.",
)
@click.option("-o", type=click.Path(), required=True, help="Output file name.")
@click.option(
    "--case", type=str, required=True, help="Name of the estimation case to run."
)
def annotate(file: Path, cd: Path, case: str, o: Path) -> None:
    """Annotate a Python source file with estimated FHE runtimes.

    FILE is the python file to look for functions decorated with
    "@dioptra_runtime" or "@dioptra_binfhe_runtime".
    """
    decorator.annotate_main(str(cd), str(file), case, str(o))


@cli.group()
def context() -> None:
    """Generate FHE runtime/memory calibration data."""
    pass


@context.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option(
    "--name",
    type=str,
    required=True,
    help="Name of the context function to generate data for.",
)
@click.option(
    "-o",
    type=click.Path(exists=False),
    required=True,
    help="File to output calibration data to.",
)
@click.option(
    "--sample-count",
    type=int,
    default=5,
    help="Number of samples to take (default: 5).",
)
def calibrate(file: Path, name: str, o: Path, sample_count: int):
    """Run calibration for a decorated context function.

    FILE is the python file to look for functions decorated with
    "@dioptra_context" or "@dioptra_binfhe_context".
    """
    decorator.context_calibrate_main([str(file)], name, str(o), sample_count)


@context.command()
@click.argument("file", type=click.Path(exists=True), required=True)
def list(file: Path):
    """List decorated context functions.

    FILE is the python file to look for functions decorated with
    "@dioptra_context" or "@dioptra_binfhe_context".
    """
    decorator.context_list_main([str(file)])
