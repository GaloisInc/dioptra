from enum import Enum
from dioptra.analyzer.utils.code_loc import Frame


class AllocationType(Enum):
    CIPHERTEXT = 1
    PLAINTEXT = 2


class MemoryReport:
    def record_setup_size(self, size: int):
        pass

    def record_alloc(
        self, ty: AllocationType, value_id: int, size: int, loc: Frame | None
    ):
        pass

    def record_dealloc(
        self, ty: AllocationType, value_id: int, size: int, loc: Frame | None
    ):
        pass


class MemoryMaxReport(MemoryReport):
    def __init__(self):
        self.setup_size = 0
        self.max_value_size = 0
        self.value_size = 0

    def record_setup_size(self, size: int):
        self.setup_size = size

    def record_alloc(
        self, ty: AllocationType, value_id: int, size: int, loc: Frame | None
    ):
        self.value_size += size
        self.max_value_size = max(self.max_value_size, self.value_size)

    def record_dealloc(
        self, ty: AllocationType, value_id: int, size: int, loc: Frame | None
    ):
        self.value_size -= size
