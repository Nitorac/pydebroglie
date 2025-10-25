from collections.abc import Iterator
from enum import Enum, IntEnum, auto
from typing import Final


class Axis(Enum):
    X = auto()
    Y = auto()
    Z = auto()
    # The "third" axis used for HEXAGONAL_2D
    # It's redundant with X and Y, but still useful to refer to.
    W = auto()


class Direction(IntEnum):
    X_PLUS = 0
    X_MINUS = 1
    Y_PLUS = 2
    Y_MINUS = 3
    Z_PLUS = 4
    Z_MINUS = 5
    # Shared with Z, there's no DirectionSet that uses both.
    W_PLUS = 4
    W_MINUS = 5


class DirectionSetType(Enum):
    """DirectionType indicates what neighbors are considered adjacent to each tile."""

    UNKNOWN = auto()
    CARTESIAN_2D = auto()
    HEXAGONAL_2D = auto()
    CARTESIAN_3D = auto()
    HEXAGONAL_3D = auto()


class EdgeLabel(Enum):
    pass


class DirectionSet:
    """Wrapper around DirectionsType supplying some convenience data."""

    def __init__(
        self,
        dx: list[int],
        dy: list[int],
        dz: list[int],
        count: int,
        mtype: DirectionSetType,
    ) -> None:
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.count = count
        self.mtype = mtype

    @staticmethod
    def inverse(d: Direction) -> Direction:
        """Given a direction, returns the direction that makes the reverse movement."""
        return Direction(int(d) ^ 1)

    def get_direction(self, x: int, y: int, z: int = 0) -> Direction:
        for d in range(self.count):
            if (x, y, z) == (self.dx[d], self.dy[d], self.dz[d]):
                return Direction(d)
        raise Exception(f"No direction corresponds to (x={x}, y={y}, z={z})")

    def __iter__(self) -> Iterator[Direction]:
        return iter(Direction(d) for d in range(self.count))


# The Directions associated with square grids.
CARTESIAN_2D: Final[DirectionSet] = DirectionSet(
    dx=[1, -1, 0, 0],
    dy=[0, 0, 1, -1],
    dz=[0, 0, 0, 0],
    count=4,
    mtype=DirectionSetType.CARTESIAN_2D,
)

# The Directions associated with hexagonal grids.
# Conventially, x is treated as moving right, and y as moving down and left,
# But the same Directions object will work just as well will several other conventions
# as long as you are consistent.
HEXAGONAL_2D: Final[DirectionSet] = DirectionSet(
    dx=[1, -1, 0, 0, 1, -1],
    dy=[0, 0, 1, -1, 1, -1],
    dz=[0, 0, 0, 0, 0, 0],
    count=6,
    mtype=DirectionSetType.HEXAGONAL_2D,
)

# The Directions associated with cubic grids.
CARTESIAN_3D: Final[DirectionSet] = DirectionSet(
    dx=[1, -1, 0, 0, 0, 0],
    dy=[0, 0, 1, -1, 0, 0],
    dz=[0, 0, 0, 0, 1, -1],
    count=6,
    mtype=DirectionSetType.CARTESIAN_3D,
)
