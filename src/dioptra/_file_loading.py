import json
import runpy

from dioptra.analyzer.binfhe.calibration import BinFHECalibrationData
from dioptra.analyzer.calibration import PKECalibrationData


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
