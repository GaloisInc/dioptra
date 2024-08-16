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
@click.argument("script", type=click.Path(exists=True))
def peakmem(script: Path) -> None:
    """Estimate peak memory usage of an OpenFHE SCRIPT."""
    click.echo("Estimating memory...")
    s = OpenFHEScript(script)
    s.show_ast()


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
    "@dioptra_runtime" or "@dioptra_binfhe_runtime".
    """
    decorator.report_main(str(calibration_data), [str(file)])


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
    "--output", "-o", type=click.Path(), required=True, help="Output file name."
)
@click.option(
    "--name",
    "-n",
    type=str,
    required=True,
    help="Name of the estimation case to annotate.",
)
def annotate(file: Path, calibration_data: Path, name: str, output: Path) -> None:
    """Annotate a Python source file with estimated FHE runtimes.

    FILE is the python file to look for functions decorated with
    "@dioptra_runtime" or "@dioptra_binfhe_runtime".
    """
    decorator.annotate_main(str(calibration_data), str(file), name, str(output))


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
    decorator.context_calibrate_main([str(file)], name, str(output), sample_count)


@context.command()
@click.argument("file", type=click.Path(exists=True), required=True)
def list(file: Path):
    """List decorated context functions.

    FILE is the python file to look for functions decorated with
    "@dioptra_context" or "@dioptra_binfhe_context".
    """
    decorator.context_list_main([str(file)])


@estimate.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--samples", type=click.Path(exists=True))
def render(file: Path, samples: Path) -> None:
    """Run decorated functions and render analysis results."""
    decorator.render_analysis(samples, [file])
