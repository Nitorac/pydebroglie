from enum import IntEnum


class Resolution(IntEnum):
    DECIDED = 0
    UNDECIDED = -1
    CONTRADICTION = -2
