from abc import ABC, abstractmethod


class ITracker(ABC):
    """
    Trackers maintain state that is a summary of the current state of the propagator.

    By updating that state as the propagator changes, they can give a significant
    performance benefit over calculating the value from scratch
    each time it is needed.
    """

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def do_ban(self, index: int, pattern: int) -> None:
        pass

    @abstractmethod
    def undo_ban(self, index: int, pattern: int) -> None:
        pass


class IChoiceObserver(ABC):
    @abstractmethod
    def make_choice(self, index: int, pattern: int) -> None:
        pass

    @abstractmethod
    def backtrack(self) -> None:
        pass
