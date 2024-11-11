from enum import Enum

from dioptra.analyzer.binfhe.calibration import BinFHECalibrationData
from dioptra.analyzer.pke.calibration import PKECalibrationData


class SchemeType(Enum):
    PKE = 1
    BINFHE = 2


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
