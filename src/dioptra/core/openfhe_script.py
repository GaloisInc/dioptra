import ast
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class OpenFHEScript:
    """An OpenFHE script.

    This is a simple wrapper around an AST, for now.
    """

    def __init__(self, script_path: Path) -> None:
        """Initialize a new OpenFHEScript."""
        self._source = script_path
        with open(script_path) as script:
            self._ast = ast.parse(script.read())

    def show_ast(self) -> None:
        """Print the OpenFHE script's AST."""
        print(ast.dump(self._ast, indent=2))
