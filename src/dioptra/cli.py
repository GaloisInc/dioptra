import click
import click_log

import logging
from pathlib import Path

from .core.openfhe_script import OpenFHEScript


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
@click.argument("script", type=click.Path(exists=True))
def runtime(script: Path) -> None:
    """Estimate the runtime of an OpenFHE SCRIPT."""
    click.echo("Estimating runtime...")
    s = OpenFHEScript(script)
    s.show_ast()
