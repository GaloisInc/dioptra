from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape


def render_results(
    outdir: str,
    file: str,
    runtime_analyses: dict[str, dict[int, str]],
) -> None:
    env = Environment(
        loader=PackageLoader("dioptra.ui"), autoescape=select_autoescape()
    )
    template = env.get_template("results_template.html")

    with (
        open(file, "r") as script,
        open(Path(outdir).joinpath(f"{Path(file).name}.html"), "w") as rendered_html,
    ):
        rendered_html.write(
            template.render(
                filename=Path(file).name,
                source=script.read(),
                analyses=runtime_analyses,
            )
        )
