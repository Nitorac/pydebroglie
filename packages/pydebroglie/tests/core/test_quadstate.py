from pydebroglie.core.quadstate import Quadstate


def test_is_yes():
    assert Quadstate.YES.is_yes()


def test_is_maybe():
    assert Quadstate.MAYBE.is_maybe()


def test_is_no():
    assert Quadstate.NO.is_no()


def test_is_contradiction():
    assert Quadstate.CONTRADICTION.is_contradiction()


def test_possible():
    assert Quadstate.YES.possible()
    assert Quadstate.MAYBE.possible()


def test_possibly_not():
    assert Quadstate.NO.possibly_not()
    assert Quadstate.MAYBE.possibly_not()
