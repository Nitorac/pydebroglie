import pytest

from pydebroglie.core.topo.directions import (
    CARTESIAN_2D,
    CARTESIAN_3D,
    HEXAGONAL_2D,
    Direction,
    DirectionSetType,
)


def test_directions():
    count2d = 4
    count3d = 6
    count2dhex = 6
    # CARTESIAN_2D
    assert CARTESIAN_2D.dx == [1, -1, 0, 0]
    assert CARTESIAN_2D.dy == [0, 0, 1, -1]
    assert CARTESIAN_2D.dz == [0, 0, 0, 0]
    assert CARTESIAN_2D.count == count2d
    assert CARTESIAN_2D.mtype == DirectionSetType.CARTESIAN_2D
    # HEXAGONAL_2D
    assert HEXAGONAL_2D.dx == [1, -1, 0, 0, 1, -1]
    assert HEXAGONAL_2D.dy == [0, 0, 1, -1, 1, -1]
    assert HEXAGONAL_2D.dz == [0, 0, 0, 0, 0, 0]
    assert HEXAGONAL_2D.count == count2dhex
    assert HEXAGONAL_2D.mtype == DirectionSetType.HEXAGONAL_2D
    # CARTESIAN_3D
    assert CARTESIAN_3D.dx == [1, -1, 0, 0, 0, 0]
    assert CARTESIAN_3D.dy == [0, 0, 1, -1, 0, 0]
    assert CARTESIAN_3D.dz == [0, 0, 0, 0, 1, -1]
    assert CARTESIAN_3D.count == count3d
    assert CARTESIAN_3D.mtype == DirectionSetType.CARTESIAN_3D


def test_direction_inverse():
    assert CARTESIAN_2D.inverse(Direction.X_PLUS) == Direction.X_MINUS
    assert CARTESIAN_2D.inverse(Direction.X_MINUS) == Direction.X_PLUS

    assert HEXAGONAL_2D.inverse(Direction.Y_PLUS) == Direction.Y_MINUS
    assert HEXAGONAL_2D.inverse(Direction.Y_MINUS) == Direction.Y_PLUS

    assert CARTESIAN_3D.inverse(Direction.Z_PLUS) == Direction.Z_MINUS
    assert CARTESIAN_3D.inverse(Direction.Z_MINUS) == Direction.Z_PLUS


def test_direction_get_set():
    assert CARTESIAN_2D.get_direction(1, 0, 0) == Direction.X_PLUS
    assert CARTESIAN_2D.get_direction(0, 1, 0) == Direction.Y_PLUS
    assert CARTESIAN_2D.get_direction(0, -1, 0) == Direction.Y_MINUS
    assert CARTESIAN_2D.get_direction(-1, 0, 0) == Direction.X_MINUS
    assert CARTESIAN_3D.get_direction(0, 0, -1) == Direction.Z_MINUS
    assert CARTESIAN_3D.get_direction(0, 0, 1) == Direction.Z_PLUS


def test_direction_get_set_invalid():
    with pytest.raises(Exception):
        CARTESIAN_2D.get_direction(0, 0, 1)


def test_direction_iterators():
    count2d = 4
    listCart2d = list(CARTESIAN_2D)
    assert len(listCart2d) == count2d
    assert listCart2d == [
        Direction.X_PLUS,
        Direction.X_MINUS,
        Direction.Y_PLUS,
        Direction.Y_MINUS,
    ]

    count3d = 6
    listCart3d = list(CARTESIAN_3D)
    assert len(listCart3d) == count3d
    assert listCart3d == [
        Direction.X_PLUS,
        Direction.X_MINUS,
        Direction.Y_PLUS,
        Direction.Y_MINUS,
        Direction.Z_PLUS,
        Direction.Z_MINUS,
    ]

    count2dhex = 6
    listHex2d = list(HEXAGONAL_2D)
    assert len(listHex2d) == count2dhex
    assert listHex2d == [
        Direction.X_PLUS,
        Direction.X_MINUS,
        Direction.Y_PLUS,
        Direction.Y_MINUS,
        Direction.W_PLUS,
        Direction.W_MINUS,
    ]
