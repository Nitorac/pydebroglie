import pytest

from pydebroglie.core.wfc.wave import Wave


def test_wave_init():
    pcount = 10
    idx = 20
    wave = Wave(pcount, idx)

    assert wave.pattern_count == pcount
    assert wave.indices == idx

    assert len(wave.possibilities) == pcount * idx
    assert sum(wave.pattern_counts) == pcount * idx


def test_wave_get_set():
    pcount = 10
    idx = 20
    wave = Wave(pcount, idx)

    wave.remove_possibility(0, 1)
    assert not wave.get(0, 1)
    wave.add_possibility(0, 1)
    assert wave.get(0, 1)


def test_wave_get_pattern_count():
    pcount = 10
    idx = 20
    wave = Wave(pcount, idx)

    assert wave.get_pattern_count(0) == pcount


def test_wave_get_progress():
    pcount = 10
    idx = 20
    wave = Wave(pcount, idx)

    assert wave.get_progress() == pytest.approx(0.0, 0.005)
    for i in range(pcount - 1):
        for j in range(idx):
            wave.remove_possibility(j, i)
    assert wave.get_progress() == pytest.approx(1.0, 0.005)


def test_wave_impossible_to_add_or_remove_twice():
    pcount = 10
    idx = 20
    wave = Wave(pcount, idx)

    wave.remove_possibility(0, 1)
    with pytest.raises(ValueError):
        wave.remove_possibility(0, 1)

    wave.add_possibility(0, 1)
    with pytest.raises(ValueError):
        wave.add_possibility(0, 1)
