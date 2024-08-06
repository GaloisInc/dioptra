from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..analyzer.metrics.analysisbase import AnalysisBase

_env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
_template = _env.get_template("results_template.html")


def render_results(analysis: AnalysisBase):
    """Render an `AnalysisBase` as an HTML document.

    The document displays the source code in a read-only text editor, and
    responds to changes in cursor position to show relevant local analysis
    results in a second column.
    """
    pass
