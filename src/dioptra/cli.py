import click
import click_log

import logging
from pathlib import Path

from dioptra import decorator
from dioptra.analyzer import calibration

from .core.openfhe_script import OpenFHEScript
from .run import passthrough


logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.group()
@click_log.simple_verbosity_option(logger)
def cli() -> None:
    """The Dioptra FHE platform."""
    pass


@cli.command()
@click.argument("script", type=click.Path(exists=True))
def run(script: Path) -> None:
    """Run an OpenFHE SCRIPT normally."""
    click.echo("Running OpenFHE program...")
    passthrough(script)


@cli.group()
def estimate() -> None:
    """Estimate properties of an OpenFHE program."""
    pass

# @estimate.command()
# @click.argument("script", type=click.Path(exists=True))
# def peakmem(script: Path) -> None:
#     """Estimate peak memory usage of an OpenFHE SCRIPT."""
#     click.echo("Estimating memory...")
#     s = OpenFHEScript(script)
#     s.show_ast()

# @estimate.command()
# @click.argument("script", type=click.Path(exists=True))
# def runtime(script: Path) -> None:
#     """Estimate the runtime of an OpenFHE SCRIPT."""
#     click.echo("Estimating runtime...")
#     s = OpenFHEScript(script)
#     s.show_ast()

@estimate.command()
@click.argument("file", type=click.Path(exists=True), required=True)
@click.option("--samples", type=click.Path(exists=True), required=True)
def report(file: Path, samples: Path) -> None:
    """Run decorated functions and report estimated runtimes"""
    decorator.report_main(str(samples), [str(file)])

@estimate.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--samples", type=click.Path(exists=True))
@click.option("--output", type=click.Path())
@click.option("--testcase", type=str)
def annotate(file: Path, samples: Path, testcase: str, output: Path) -> None:
    """Run decorated functions and report estimated runtimes"""
    decorator.annotate_main(str(samples), str(file), testcase, str(output))


@cli.group()
def context() -> None:
    """Information about OpenFHE contexts"""
    pass

@context.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-n", type=str, required=True)
@click.option("-o", type=click.Path(exists=False), required=True)
@click.option("-c", type=int, default=5)
def calibrate(file: Path, n: str, o: Path, c: int):
    decorator.context_calibrate_main([str(file)], n, str(o), c)

@context.command()
@click.argument("file", type=click.Path(exists=True))
def list(file: Path):
    decorator.context_list_main([str(file)])


# @click.option("-o", type=click.Path(writable=True))
# def annotate(file: Path, function: str, s: str):
#     decorator.annotate(file, function, s)
