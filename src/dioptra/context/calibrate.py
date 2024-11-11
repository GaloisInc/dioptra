import sys

from dioptra._file_loading import load_files
from dioptra.binfhe.calibration import BinFHECalibration
from dioptra.pke.calibration import PKECalibration
from dioptra.context import context_functions
from dioptra.scheme_type import SchemeType


def calibrate_main(
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
