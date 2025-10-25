from abc import ABC, abstractmethod


class IPatternModelConstraint(ABC):
    """
    Similar to IWaveConstraint.

    This listens to changes in the Wave and makes
    appropriate changes to the propagator for the constraint.
    It's special mostly for historical reasons, and is used for the adjacent
    pattern constraint specified by the model.
    """

    @abstractmethod
    def do_ban(self, index: int, pattern: int) -> None:
        pass

    @abstractmethod
    def undo_ban(self, index: int, pattern: int) -> None:
        pass

    @abstractmethod
    def do_select(self, index: int, pattern: int) -> None:
        pass

    @abstractmethod
    def propagate(self) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
