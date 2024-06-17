import subprocess
from pathlib import Path


def passthrough(script: Path) -> None:
    subprocess.run(["python", script])
