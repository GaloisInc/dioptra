import json
from os import path
import runpy
import sys

from dioptra.binfhe.calibration import BinFHECalibrationData
from dioptra.pke.calibration import PKECalibrationData


def load_files(files: list[str]) -> None:
    for file in files:
        p = list(sys.path)
        sys.path.append(path.dirname(file))
        runpy.run_path(file)
        sys.path = p


def load_calibration_data(file: str) -> PKECalibrationData | BinFHECalibrationData:
    with open(file) as handle:
        obj = json.load(handle)
        if obj["scheme"]["name"] == "BINFHE":
            return BinFHECalibrationData.from_dict(obj)
        else:
            return PKECalibrationData.from_dict(obj)
