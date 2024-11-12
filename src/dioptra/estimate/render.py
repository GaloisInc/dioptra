import importlib.resources as ilr
import os
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

import dioptra
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.binfhe.calibration import BinFHECalibrationData
from dioptra.binfhe.runtime import RuntimeEstimate
from dioptra.estimate import estimation_cases
from dioptra.pke.analyzer import Analyzer
from dioptra.pke.calibration import PKECalibrationData
from dioptra.pke.runtime import Runtime
from dioptra.report.runtime import RuntimeAnnotation
from dioptra.utils.code_loc import TraceLoc
from dioptra.utils.file_loading import load_calibration_data, load_files
from dioptra.utils.measurement import format_ns
from dioptra.utils.scheme_type import SchemeType, calibration_type

SKELETON_DIR = "analysis_site_skeleton"


def render_main(sample_file: str, file: str, test_case: str, output: str) -> None:
    with ilr.as_file(ilr.files(dioptra.estimate).joinpath(SKELETON_DIR)) as p:
        shutil.copytree(p, output, dirs_exist_ok=True)

    calibration = load_calibration_data(sample_file)
    load_files([file])
    case = estimation_cases.get(test_case)

    if case is None:
        print(
            f"ERROR: Cound not find test case '{test_case}' in scope", file=sys.stderr
        )
        return

    runtime_analyses: dict[str, dict[int, str]] = {}
    if case.schemetype == SchemeType.PKE and isinstance(
        calibration, PKECalibrationData
    ):
        annot_rpt = RuntimeAnnotation()
        runtime_analysis = Runtime(calibration, annot_rpt)

        with TraceLoc() as tloc:
            analyzer = Analyzer([runtime_analysis], calibration.get_scheme(), tloc)
            case.run_and_exit_if_unsupported(analyzer)

            for fname, annotation in annot_rpt.annotation_dicts():
                time_lookup: dict[int, str] = {
                    k - 1: format_ns(v) for k, v in annotation.items()
                }
                runtime_analyses[fname] = time_lookup

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

            for fname, annotation in annot_rpt.annotation_dicts():
                time_lookup: dict[int, str] = {
                    k - 1: format_ns(v) for k, v in annotation.items()
                }
                runtime_analyses[fname] = time_lookup

    else:
        print(
            f"[FAIL---] {case.description}: Cannot run case with this calibration data"
        )
        print(
            f"          Calibration is for a {calibration_type(calibration).name} context"
        )
        print(f"          But estimation case requires a {case.schemetype} context")
        return

    render_results(output, test_case, runtime_analyses)


def render_results(
    outdir: str,
    test_case: str,
    runtime_analyses: dict[str, dict[int, str]],
) -> None:
    env = Environment(
        loader=PackageLoader("dioptra.estimate"), autoescape=select_autoescape()
    )
    template = env.get_template("results_template.html")

    case_root = Path(os.path.commonprefix(list(runtime_analyses.keys())))
    sources = {}
    analyses = {}
    for fname in runtime_analyses:
        with open(fname) as f:
            f = f.read()

        if os.path.isdir(case_root):
            simple_name = str(Path(fname).relative_to(case_root))
        else:
            simple_name = str(Path(fname).name)

        sources[simple_name] = f
        analyses[simple_name] = runtime_analyses[fname]

    with open(Path(outdir).joinpath(f"{test_case}.html"), "w") as rendered_html:
        rendered_html.write(
            template.render(
                test_case=test_case,
                sources=sources,
                analyses=analyses,
            )
        )
