import os
import sys
from pathlib import Path

from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.binfhe.calibration import BinFHECalibrationData
from dioptra.binfhe.runtime import RuntimeEstimate
from dioptra.estimate import estimation_cases
from dioptra.pke.analyzer import Analyzer
from dioptra.pke.calibration import PKECalibrationData
from dioptra.pke.runtime import Runtime
from dioptra.report.runtime import RuntimeAnnotation
from dioptra.utils.file_loading import load_calibration_data, load_files
from dioptra.utils.measurement import format_ns
from dioptra.utils.scheme_type import SchemeType


def annotate_main(sample_file: str, file: str, test_case: str, output: str) -> None:
    calibration = load_calibration_data(sample_file)
    load_files([file])
    case = estimation_cases.get(test_case, None)

    if case is None:
        print(
            f"ERROR: Could not find test case '{test_case}' in scope", file=sys.stderr
        )
        return

    if case.schemetype == SchemeType.PKE and isinstance(
        calibration, PKECalibrationData
    ):
        annot_rpt = RuntimeAnnotation()
        runtime_analysis = Runtime(calibration, annot_rpt)
        analyzer = Analyzer([runtime_analysis], calibration.scheme)
        case.run_and_exit_if_unsupported(analyzer)

        case_root = Path(
            os.path.commonprefix([case[0] for case in annot_rpt.annotation_dicts()])
        )

        case_output = Path(output)
        if os.path.isdir(case_root):
            case_output = case_output.joinpath(case_root.stem)
        os.makedirs(case_output, exist_ok=True)

        for fname, annotation in annot_rpt.annotation_dicts():
            if os.path.isdir(case_root):
                fname_out = case_output.joinpath(Path(fname).relative_to(case_root))
            else:
                fname_out = case_output.joinpath(Path(fname).name)

            os.makedirs(fname_out.parent, exist_ok=True)

            annotation = {line: format_ns(ns) for (line, ns) in annotation.items()}
            annotate_lines(
                fname,
                fname_out,
                annotation,
            )

    elif case.schemetype == SchemeType.BINFHE and isinstance(
        calibration, BinFHECalibrationData
    ):
        annot_rpt = RuntimeAnnotation()
        est = RuntimeEstimate(
            calibration.avg_case(), calibration.ciphertext_size, annot_rpt
        )
        analyzer = BinFHEAnalyzer(calibration.params, est)
        case.run_and_exit_if_unsupported(analyzer)

        case_root = Path(
            os.path.commonprefix([case[0] for case in annot_rpt.annotation_dicts()])
        )

        case_output = Path(output)
        if os.path.isdir(case_root):
            case_output = case_output.joinpath(case_root.stem)
        os.makedirs(case_output, exist_ok=True)

        for fname, annotation in annot_rpt.annotation_dicts():
            if os.path.isdir(case_root):
                fname_out = case_output.joinpath(Path(fname).relative_to(case_root))
            else:
                fname_out = case_output.joinpath(Path(fname).name)

            os.makedirs(fname_out.parent, exist_ok=True)

            annotation = {line: format_ns(ns) for (line, ns) in annotation.items()}
            annotate_lines(
                fname,
                fname_out,
                annotation,
            )

    else:
        print(
            f"Calibration data '{sample_file}' is not compatible with estimation case '{test_case}'"
        )


def annotate_lines(infile: str, outfile: str, annotation: dict[int, str]):
    line_number = 1
    with open(infile) as inf:
        with open(outfile, "w") as outf:
            for line in inf:
                line = line.rstrip()
                ann = annotation.get(line_number, None)
                if ann is not None:
                    print(f"{line.rstrip()} # {ann}", file=outf)
                else:
                    print(line, file=outf)

                line_number += 1
