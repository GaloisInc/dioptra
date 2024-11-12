import inspect

from dioptra.context import context_functions
from dioptra.utils.file_loading import load_files


def list_main(files: list[str]):
    load_files(files)

    for cf in context_functions.values():
        file = inspect.getfile(cf.run)
        (_, line) = inspect.getsourcelines(cf.run)
        print(f"{cf.description} (defined at {file}:{line})")
