import inspect

from dioptra._file_loading import load_files
from dioptra.context import context_functions


def list_main(files: list[str]):
    load_files(files)

    for cf in context_functions.values():
        file = inspect.getfile(cf.run)
        (_, line) = inspect.getsourcelines(cf.run)
        print(f"{cf.description} (defined at {file}:{line})")
