import datetime
from enum import Enum
import importlib.util
import inspect
import json
from multiprocessing import Value
from plistlib import InvalidFileException
import runpy
import sys
from typing import Callable, OrderedDict

from dioptra.analyzer.binfhe import memory
from dioptra.analyzer.binfhe.analyzer import BinFHEAnalysisGroup, BinFHEAnalyzer
from dioptra.analyzer.binfhe.calibration import BinFHECalibration, BinFHECalibrationData
from dioptra.analyzer.binfhe.memory import BinFHEMemoryEstimate
from dioptra.analyzer.binfhe.runtime import RuntimeEstimate
from dioptra.analyzer.calibration import PKECalibration, PKECalibrationData
from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.memory import PKEMemoryEstimate, PKEMemoryEstimate
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.report.memory import MemoryMaxReport
from dioptra.analyzer.report.runtime import RuntimeAnnotation, RuntimeTotal
from dioptra.analyzer.utils.code_loc import TraceLoc
from dioptra.analyzer.utils.util import format_bytes, format_ns, format_ns_approx
from dioptra.analyzer.utils.error import NotSupportedException
from dioptra.visualization.annotation import annotate_lines


# TODO: does this belong somewhere accessible more places
class SchemeType(Enum):
    PKE = 1
    BINFHE = 2


class EstimationCase:
    def __init__(
        self,
        desc: str,
        f: Callable,
        schemetype: SchemeType,
        limit: datetime.timedelta | None,
    ):
        self.description = desc
        self.run = f
        self.schemetype = schemetype
        self.limit = limit

    def run_and_exit_if_unsupported(self, a: Analyzer | BinFHEAnalyzer) -> None:
        try:
            self.run(a)
        except NotSupportedException as e:
            print("Analysis failed:")
            print(f"  { e.display()}")
            sys.exit(1)


class ContextFunction:
    def __init__(self, desc: str, f: Callable, schemetype: SchemeType):
        self.description = desc
        self.run = f
        self.schemetype = schemetype


context_functions: OrderedDict[str, ContextFunction] = OrderedDict()
estimation_cases: OrderedDict[str, EstimationCase] = OrderedDict()


def estimation_case_decorator(
    description: str | None,
    f: Callable,
    limit: datetime.timedelta | None,
    ty: SchemeType,
) -> Callable:
    d = f.__name__ if description is None else description
    if d in estimation_cases:
        other = estimation_cases[d]
        file = inspect.getfile(other.run)
        (_, line) = inspect.getsourcelines(other.run)
        raise ValueError(
            f"Estimation case {d} has been defined earlier (at  ={file}:{line}) - use 'description' in decorator to rename?"
        )

    estimation_cases[d] = EstimationCase(d, f, ty, limit)
    return f


def dioptra_runtime(
    limit: datetime.timedelta | None = None, description: str | None = None
) -> Callable:  # TODO better type
    def decorator(f):
        estimation_case_decorator(description, f, limit, SchemeType.PKE)

    return decorator


def dioptra_binfhe_runtime(
    limit: datetime.timedelta | None = None, description: str | None = None
) -> Callable:  # TODO better type
    def decorator(f):
        estimation_case_decorator(description, f, limit, SchemeType.BINFHE)

    return decorator


def timedelta_as_ns(d: datetime.timedelta) -> int:
    return d.microseconds * (10**3) + d.seconds * (10**9) + d.days * 24 * 3600 * (10**9)


def annotate(file: str, function: str, outdir: str):
    pass


def load_files(files: list[str]) -> None:
    for file in files:
        runpy.run_path(file)


def load_calibration_data(file: str) -> PKECalibrationData | BinFHECalibrationData:
    with open(file) as handle:
        obj = json.load(handle)
        if obj["scheme"]["name"] == "BINFHE":
            return BinFHECalibrationData.from_dict(obj)
        else:
            return PKECalibrationData.from_dict(obj)


def calibration_type(
    calibration: PKECalibrationData | BinFHECalibrationData,
) -> SchemeType:
    if isinstance(calibration, PKECalibrationData):
        return SchemeType.PKE

    elif isinstance(calibration, BinFHECalibrationData):
        return SchemeType.BINFHE

    else:
        raise NotImplementedError(
            f"Cannot determine scheme type for calibration: {type(calibration)}"
        )


def report_main(sample_file: str, files: list[str]) -> None:
    calibration = load_calibration_data(sample_file)

    load_files(files)

    for case in estimation_cases.values():
        runtime = None
        maxmem = MemoryMaxReport()

        if case.schemetype == SchemeType.PKE and isinstance(
            calibration, PKECalibrationData
        ):
            total = RuntimeTotal()
            runtime_analysis = Runtime(calibration, total)
            memory_analysis = PKEMemoryEstimate(
                calibration.setup_memory_size,
                calibration.ct_mem,
                calibration.pt_mem,
                maxmem,
            )

            with TraceLoc() as tloc:
                analyzer = Analyzer(
                    [runtime_analysis, memory_analysis], calibration.get_scheme(), tloc
                )
                case.run_and_exit_if_unsupported(analyzer)
                runtime = runtime_analysis.total_runtime

        elif case.schemetype == SchemeType.BINFHE and isinstance(
            calibration, BinFHECalibrationData
        ):
            avg_runtime = calibration.avg_case()
            total = RuntimeTotal()
            runtime_analysis = RuntimeEstimate(
                avg_runtime, calibration.ciphertext_size, total
            )
            memory_analysis = BinFHEMemoryEstimate(
                calibration.setup_memory_size, calibration.ciphertext_size, maxmem
            )
            with TraceLoc() as tloc:
                analyzer = BinFHEAnalyzer(
                    calibration.params,
                    BinFHEAnalysisGroup([runtime_analysis, memory_analysis]),
                    tloc,
                )
                case.run_and_exit_if_unsupported(analyzer)
                runtime = total.total_runtime

        else:
            print(
                f"[FAIL---] {case.description}: Cannot run case with this calibration data"
            )
            print(
                f"          Calibration is for a {calibration_type(calibration).name} context"
            )
            print(f"          But estimation case requires a {case.schemetype} context")
            continue

        if case.limit is None:
            status = "[-------]"

        elif runtime <= timedelta_as_ns(case.limit):
            status = "[OK     ]"

        else:
            status = "[TIMEOUT]"

        total = maxmem.max_value_size + maxmem.setup_size
        print(f"{status } {case.description}")
        print(f"  Runtime:     { format_ns_approx(runtime) }")
        print(f"  Max Memory:  { format_bytes(total) }")


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
        annotation = runtime_analysis.annotation_dict(file)
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


def dioptra_context_decorator(
    description: str | None, f: Callable, ty: SchemeType
) -> Callable:
    d = f.__name__ if description is None else description
    if d in context_functions:
        other = estimation_cases[d]
        file = inspect.getfile(other.run)
        (_, line) = inspect.getsourcelines(other.run)
        raise ValueError(
            f"Context {d} has been defined earlier (at  ={file}:{line}) - use 'description' in decorator to rename?"
        )

    context_functions[d] = ContextFunction(d, f, ty)
    return f


def dioptra_context(description: str | None = None):
    def decorator(f):
        return dioptra_context_decorator(description, f, SchemeType.PKE)

    return decorator


def dioptra_binfhe_context(description: str | None = None):
    def decorator(f):
        return dioptra_context_decorator(description, f, SchemeType.BINFHE)

    return decorator


def context_list_main(files: list[str]):
    load_files(files)

    for cf in context_functions.values():
        file = inspect.getfile(cf.run)
        (_, line) = inspect.getsourcelines(cf.run)
        print(f"{cf.description} (defined at {file}:{line})")


def context_calibrate_main(
    files: list[str], name: str, outfile: str, samples: int = 5, quiet: bool = False
):
    load_files(files)

    cf = context_functions.get(name, None)
    if cf is None:
        print(f"Calibration failed: no context named '{name}' found", file=sys.stderr)
        sys.exit(-1)

    print(f"Calibration for f{cf.schemetype} scheme")
    if cf.schemetype == SchemeType.PKE:
        (cc, params, key_pair, features) = cf.run()
        log = None if quiet else sys.stdout
        calibration = PKECalibration(
            cc, params, key_pair, features, log, sample_count=samples
        )
        smp = calibration.calibrate()
        smp.write_json(outfile)

    elif cf.schemetype == SchemeType.BINFHE:
        (cc, sk) = cf.run()
        log = None if quiet else sys.stdout
        calibration = BinFHECalibration(cc, sk, log=log, sample_count=samples)
        cd = calibration.run()
        cd.write_json(outfile)
