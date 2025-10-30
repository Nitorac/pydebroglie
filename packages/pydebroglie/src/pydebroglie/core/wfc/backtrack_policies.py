from abc import ABC, abstractmethod

from pydebroglie.core.wfc.wave_propagator import WavePropagator


class IBacktrackPolicy(ABC):
    @abstractmethod
    def init(self, wavepropagator: WavePropagator) -> None:
        pass

    @abstractmethod
    def get_backjump(self) -> int:
        pass


class ConstantBacktrackPolicy(IBacktrackPolicy):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def init(self, wavepropagator: WavePropagator) -> None:
        pass

    def get_backjump(self) -> int:
        return self.amount


# @TODO: Add all others backtrack policies
