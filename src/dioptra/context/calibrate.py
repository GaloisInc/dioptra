from collections import OrderedDict
import sys
from typing import Any

from dioptra.binfhe.calibration import BinFHECalibration
from dioptra.context import context_functions
from dioptra.pke.calibration import PKECalibration
from dioptra.utils.file_loading import load_files
from dioptra.utils.scheme_type import SchemeType


def calibrate_main(
    files: list[str], name: str, outfile: str, samples: int = 5, quiet: bool = False, meta_file = str | None
):
    load_files(files)

    meta_file_data = None
    if meta_file is not None:
        with open(meta_file) as f:
            meta_file_data = f.read()


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
        meta = format_meta(cf.description, meta_file_data, calibration.gen_metadata())
        smp.metadata = meta
        smp.write_json(outfile)

    elif cf.schemetype == SchemeType.BINFHE:
        (cc, sk) = cf.run()
        log = None if quiet else sys.stdout
        calibration = BinFHECalibration(cc, sk, log=log, sample_count=samples)
        cd = calibration.run()
        meta = format_meta(cf.description, meta_file_data, calibration.gen_metadata())
        cd.metadata = meta
        cd.write_json(outfile)

def format_meta(desc: str, mf: str|None, gen: OrderedDict[str, Any]) -> str:
    metas = [("description", desc)] + list(gen.items())
    output = ""
    for (n,v) in metas:
        output = output + f"{n}: {v}\n"

    if mf is not None:
        output += "\n"
        output += mf
    
    return output


