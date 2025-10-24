from abc import ABC, abstractmethod
from collections.abc import Callable

from pydebroglie.core.wfc.WavePropagator import WavePropagator


class IPatternPicker(ABC):
    @abstractmethod
    def init(self, wave_propagator: WavePropagator) -> None:
        pass

    @abstractmethod
    def get_random_possible_pattern_at(
        self, index: int, random_double: Callable[[], float]
    ) -> int:
        pass
