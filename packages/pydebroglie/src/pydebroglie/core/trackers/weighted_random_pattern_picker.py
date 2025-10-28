from collections.abc import Callable

from pydebroglie.core.trackers.pattern_picker import IPatternPicker
from pydebroglie.core.trackers.random_picker_utils import RandomPickerUtils
from pydebroglie.core.wfc.wave import Wave
from pydebroglie.core.wfc.wave_propagator import WavePropagator


class WeightedRandomPatternPicker(IPatternPicker):
    wave: Wave
    frequencies: list[float]

    def init(self, wave_propagator: WavePropagator) -> None:
        if wave_propagator.wave is None:
            raise Exception("Wave should not be None")
        self.wave = wave_propagator.wave
        self.frequencies = wave_propagator.frequencies

    def get_random_possible_pattern_at(
        self, index: int, random_double: Callable[[], float]
    ) -> int:
        return RandomPickerUtils.get_random_possible_pattern(
            self.wave, random_double, index, self.frequencies, None
        )
