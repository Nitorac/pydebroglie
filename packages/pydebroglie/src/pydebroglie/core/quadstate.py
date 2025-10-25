from enum import Enum


class Quadstate(Enum):
    CONTRADICTION = -2
    NO = -1
    MAYBE = 0
    YES = 1

    def is_yes(self) -> bool:
        return self == Quadstate.YES

    def is_maybe(self) -> bool:
        return self == Quadstate.MAYBE

    def is_no(self) -> bool:
        return self == Quadstate.NO

    def is_contradiction(self) -> bool:
        return self == Quadstate.CONTRADICTION

    def possible(self) -> bool:
        return self.value >= 0

    def possibly_not(self) -> bool:
        return self in (Quadstate.NO, Quadstate.MAYBE)
