from pydebroglie.core.quadstate import Quadstate


def test_is_yes():
    if not Quadstate.YES.is_yes():
        raise AssertionError("DEV ERROR: Should not happen Quadstate.YES is not YES")


def test_is_maybe():
    if not Quadstate.MAYBE.is_maybe():
        raise AssertionError("DEV ERROR: Should not happen Quadstate.MAYBE is not MAYBE")


def test_is_no():
    if not Quadstate.NO.is_no():
        raise AssertionError("DEV ERROR: Should not happen Quadstate.NO is not NO")


def test_is_contradiction():
    if not Quadstate.CONTRADICTION.is_contradiction():
        raise AssertionError(
            "DEV ERROR: Should not happen Quadstate.CONTRADICTION is not CONTRADICTION"
        )


def test_possible():
    if not Quadstate.YES.possible():
        raise AssertionError("DEV ERROR: Should not happen Quadstate.YES is not possible")
    if not Quadstate.MAYBE.possible():
        raise AssertionError(
            "DEV ERROR: Should not happen Quadstate.MAYBE is not possible"
        )


def test_possibly_not():
    if not Quadstate.NO.possibly_not():
        raise AssertionError(
            "DEV ERROR: Should not happen Quadstate.NO is not possibly_not"
        )
    if not Quadstate.MAYBE.possibly_not():
        raise AssertionError(
            "DEV ERROR: Should not happen Quadstate.MAYBE is not possibly_not"
        )
