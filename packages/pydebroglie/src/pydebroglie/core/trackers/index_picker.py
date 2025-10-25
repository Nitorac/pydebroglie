from abc import ABC, abstractmethod
from collections.abc import Callable

from pydebroglie.core.wfc.wave_propagator import WavePropagator


class IIndexPicker(ABC):
    @abstractmethod
    def init(self, wave_propagator: WavePropagator) -> None:
        pass

    @abstractmethod
    def get_random_index(self, random_double: Callable[[], float]) -> int:
        pass


class IFilteredIndexPicker(ABC):
    @abstractmethod
    def init(self, wave_propagator: WavePropagator) -> None:
        pass

    @abstractmethod
    def get_random_index_with_indicies(
        self, random_double: Callable[[], float], indices: list[int]
    ) -> int:
        pass
