from abc import ABC, abstractmethod

from pydebroglie.core.wfc.wave_propagator import WavePropagator


class IWaveConstraint(ABC):
    @abstractmethod
    def init(self, wave_propagator: WavePropagator) -> None:
        pass

    @abstractmethod
    def check(self, wave_propagator: WavePropagator) -> None:
        pass
