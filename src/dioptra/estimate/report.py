from dioptra._file_loading import load_calibration_data, load_files
from dioptra.analyzer.binfhe.analyzer import BinFHEAnalysisGroup, BinFHEAnalyzer
from dioptra.analyzer.binfhe.calibration import BinFHECalibrationData
from dioptra.analyzer.binfhe.memory import BinFHEMemoryEstimate
from dioptra.analyzer.binfhe.runtime import RuntimeEstimate
from dioptra.analyzer.pke.analysisbase import Analyzer
from dioptra.analyzer.pke.calibration import PKECalibrationData
from dioptra.analyzer.pke.memory import PKEMemoryEstimate
from dioptra.analyzer.pke.runtime import Runtime
from dioptra.analyzer.report.memory import MemoryMaxReport
from dioptra.analyzer.report.runtime import RuntimeTotal
from dioptra.analyzer.utils.code_loc import TraceLoc
from dioptra.analyzer.utils.util import format_bytes, format_ns_approx, timedelta_as_ns
from dioptra.estimate import estimation_cases
from dioptra.scheme_type import SchemeType, calibration_type


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
                runtime = total.total_runtime

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
