from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape


def render_results(
    outdir: Path,
    file: Path,
    runtime_analyses: dict[str, dict[tuple[int, int, int, int], str]],
) -> None:
    env = Environment(
        loader=PackageLoader("dioptra.ui"), autoescape=select_autoescape()
    )
    template = env.get_template("results_template.html")

    with open(file, "r") as script, open(
        outdir.joinpath(f"{file.name}.html"), "w"
    ) as rendered_html:
        rendered_html.write(
            template.render(
                filename=file.name,
                source=script.read(),
                analyses=runtime_analyses,
            )
        )
