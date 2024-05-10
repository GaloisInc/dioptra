import click
import click_log

import logging


logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.group()
@click_log.simple_verbosity_option(logger)
def cli() -> None:
    """The Dioptra FHE platform."""
    pass


@cli.command()
@click.argument("script", type=click.Path(exists=True))
def run(script: click.Path) -> None:
    """Run an OpenFHE program normally."""
    click.echo("Running OpenFHE program...")


@cli.group()
def estimate() -> None:
    """Estimate properties of an OpenFHE program."""
    pass


@estimate.command()
@click.argument("script", type=click.File("r"))
def peakmem(script: click.File) -> None:
    """Estimate peak memory usage of an OpenFHE program."""
    click.echo("Estimating memory...")


@estimate.command()
@click.argument("script", type=click.File("r"))
def runtime(script: click.File) -> None:
    """Estimate the runtime of an OpenFHE program."""
    click.echo("Estimating runtime...")
