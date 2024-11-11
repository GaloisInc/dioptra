import sys

from dioptra._file_loading import load_calibration_data, load_files
from dioptra.binfhe.analyzer import BinFHEAnalyzer
from dioptra.binfhe.calibration import BinFHECalibrationData
from dioptra.binfhe.runtime import RuntimeEstimate
from dioptra.estimate import estimation_cases
from dioptra.pke.analyzer import Analyzer
from dioptra.pke.calibration import PKECalibrationData
from dioptra.pke.runtime import Runtime
from dioptra.report.runtime import RuntimeAnnotation
from dioptra.scheme_type import SchemeType
from dioptra.utils.measurement import format_ns


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
        annotation = dict(
            (line, format_ns(ns))
            for (line, ns) in annot_rpt.annotation_for(file).items()
        )
        annotate_lines(file, output, annotation)

    elif case.schemetype == SchemeType.BINFHE and isinstance(
        calibration, BinFHECalibrationData
    ):
        annot_rpt = RuntimeAnnotation()
        est = RuntimeEstimate(
            calibration.avg_case(), calibration.ciphertext_size, annot_rpt
        )
        analyzer = BinFHEAnalyzer(calibration.params, est)
        case.run_and_exit_if_unsupported(analyzer)
        annotation = dict(
            (line, format_ns(ns))
            for (line, ns) in annot_rpt.annotation_for(file).items()
        )
        annotate_lines(file, output, annotation)

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
