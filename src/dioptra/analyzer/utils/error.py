from dioptra.analyzer.utils.code_loc import Frame, MaybeFrame, calling_frame


class NotSupportedException(Exception):
    def __init__(self, what: str, where: Frame | None):
        super().__init__(what)
        self.what = what
        self.where = MaybeFrame(where)

    @staticmethod
    def fn_not_impl(
        fn_name: str,
        where: Frame | None = MaybeFrame.current().caller().caller().get_frame(),
    ):
        msg = f"Method '{fn_name}' is not supported for analysis in the current version of dioptra"
        return NotSupportedException(msg, where)

    def display(self) -> str:
        return f"{self.where.source_location()} : {self.what}"
