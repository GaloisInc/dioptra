import importlib.resources as ilr
import shutil
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

import dioptra
from dioptra._file_loading import load_calibration_data, load_files
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.binfhe.calibration import BinFHECalibrationData
from dioptra.binfhe.runtime import RuntimeEstimate
from dioptra.pke.analysisbase import Analyzer
from dioptra.pke.calibration import PKECalibrationData
from dioptra.pke.runtime import Runtime
from dioptra.report.runtime import RuntimeAnnotation
from dioptra.utils.code_loc import TraceLoc
from dioptra.utils.util import format_ns
from dioptra.estimate import estimation_cases
from dioptra.scheme_type import SchemeType, calibration_type

SKELETON_DIR = "analysis_site_skeleton"


def render_main(sample_file: str, file: str, output: str) -> None:
    with ilr.as_file(ilr.files(dioptra.estimate).joinpath(SKELETON_DIR)) as p:
        shutil.copytree(p, output, dirs_exist_ok=True)

    calibration = load_calibration_data(sample_file)

    load_files([file])

    runtime_analyses: dict[str, dict[int, str]] = {}
    for case in estimation_cases.values():
        if case.schemetype == SchemeType.PKE and isinstance(
            calibration, PKECalibrationData
        ):
            annot_rpt = RuntimeAnnotation()
            runtime_analysis = Runtime(calibration, annot_rpt)

            with TraceLoc() as tloc:
                analyzer = Analyzer([runtime_analysis], calibration.get_scheme(), tloc)
                case.run_and_exit_if_unsupported(analyzer)

                # Map lines to time
                time_lookup: dict[int, str] = {
                    k - 1: format_ns(v)
                    for (k, v) in annot_rpt.annotation_for(file).items()
                }

                runtime_analyses[case.run.__name__] = time_lookup

        elif case.schemetype == SchemeType.BINFHE and isinstance(
            calibration, BinFHECalibrationData
        ):
            annot_rpt = RuntimeAnnotation()
            est = RuntimeEstimate(
                calibration.avg_case(), calibration.ciphertext_size, annot_rpt
            )
            with TraceLoc() as tloc:
                analyzer = BinFHEAnalyzer(
                    calibration.params,
                    est,
                    tloc,
                )
                case.run_and_exit_if_unsupported(analyzer)

                # Map lines to time
                time_lookup: dict[int, str] = {
                    k - 1: format_ns(v)
                    for (k, v) in annot_rpt.annotation_for(file).items()
                }

                runtime_analyses[case.run.__name__] = time_lookup
        else:
            print(
                f"[FAIL---] {case.description}: Cannot run case with this calibration data"
            )
            print(
                f"          Calibration is for a {calibration_type(calibration).name} context"
            )
            print(f"          But estimation case requires a {case.schemetype} context")
            continue

    render_results(output, file, runtime_analyses)


def render_results(
    outdir: str,
    file: str,
    runtime_analyses: dict[str, dict[int, str]],
) -> None:
    env = Environment(
        loader=PackageLoader("dioptra.estimate"), autoescape=select_autoescape()
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
