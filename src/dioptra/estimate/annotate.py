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

def annotate_main(sample_file: str, file: str, test_case: str, output: str, ann_root_str: str) -> None:
    calibration = load_calibration_data(sample_file)
    load_files([file])
    case = estimation_cases.get(test_case, None)

    if case is None:
        print(
            f"ERROR: Could not find test case '{test_case}' in scope", file=sys.stderr
        )
        return
    
    ann_root = Path(ann_root_str).absolute()
    if not ann_root.exists():
        print(f"Annotation root must be an existing directory - could not find '{ann_root_str}'", file=sys.stderr)
        return
    
    if not ann_root.is_dir():
        print(f"Annotation root must be an existing directory - '{ann_root_str}' is not a directory", file=sys.stderr)
        return

    case_output = Path(output)

    annot_rpt = None
    if case.schemetype == SchemeType.PKE and isinstance(
        calibration, PKECalibrationData
    ):
        annot_rpt = RuntimeAnnotation()
        runtime_analysis = Runtime(calibration, annot_rpt)
        analyzer = Analyzer([runtime_analysis], calibration.scheme)
        case.run_and_exit_if_unsupported(analyzer)


    elif case.schemetype == SchemeType.BINFHE and isinstance(
        calibration, BinFHECalibrationData
    ):
        annot_rpt = RuntimeAnnotation()
        est = RuntimeEstimate(
            calibration.avg_case(), calibration.ciphertext_size, annot_rpt
        )
        analyzer = BinFHEAnalyzer(calibration.params, est)
        case.run_and_exit_if_unsupported(analyzer)


    else:
        print(
            f"Calibration data '{sample_file}' is not compatible with estimation case '{test_case}'"
        )
        return

    for fname, annotation in annot_rpt.annotation_dicts():
        fpath = Path(fname).absolute()
        if ann_root in fpath.parents:
            fname_out = case_output.joinpath(fpath.relative_to(ann_root))
            print(fname_out)
            os.makedirs(fname_out.parent, exist_ok=True)

            annotation = {line: format_ns(ns) for (line, ns) in annotation.items()}
            annotate_lines(
                fname,
                fname_out,
                annotation,
            )
        else:
            print(f"Skipping {fname} - not in scope wrt {ann_root}.")

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
