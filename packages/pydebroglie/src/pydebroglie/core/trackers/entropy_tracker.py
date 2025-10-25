import math
from collections.abc import Callable, Iterable
from copy import copy
from dataclasses import dataclass
from typing import Self

from bitarray import bitarray

from pydebroglie.core.trackers.index_picker import IFilteredIndexPicker, IIndexPicker
from pydebroglie.core.trackers.tracker import ITracker
from pydebroglie.core.wfc.wave import Wave
from pydebroglie.core.wfc.wave_propagator import WavePropagator


@dataclass
class EntropyValues:
    """
    Struct containing the values needed to compute the entropy of all the cells.

    This struct is updated every time the cell is changed.
    p'(pattern) is equal to Frequencies[pattern] if the pattern is still possible,
    otherwise 0.
    """

    # The sum of p'(pattern) * log(p'(pattern)).
    p_logp_sum: float

    # The sum of p'(pattern).
    psum: float

    # The entropy of the cell.
    entropy: float

    def recompute_entropy(self) -> None:
        self.entropy = math.log1p(self.psum) - self.p_logp_sum / self.psum

    def decrement(self, p: float, p_logp: float) -> None:
        self.p_logp_sum -= p_logp
        self.psum -= p
        self.recompute_entropy()

    def increment(self, p: float, p_logp: float) -> None:
        self.p_logp_sum += p_logp
        self.psum += p
        self.recompute_entropy()

    def __copy__(self) -> Self:
        return type(self)(
            p_logp_sum=self.p_logp_sum, psum=self.psum, entropy=self.entropy
        )


class EntropyTracker(ITracker, IIndexPicker, IFilteredIndexPicker):
    pattern_count: int
    frequencies: list[float]

    # Track some useful per-cell values
    entropy_values: list[EntropyValues]

    # See the definition in EntropyValues
    p_logp: list[float]

    mask: bitarray | None
    indices: int
    wave: Wave

    def reset(self) -> None:
        """Assumes reset is called on a truly new Wave."""
        initial: EntropyValues = EntropyValues(
            p_logp_sum=0,
            psum=0,
            entropy=0,
        )
        for pattern in range(self.pattern_count):
            f = self.frequencies[pattern]
            v = f * math.log1p(f) if f > 0 else 0.0
            initial.p_logp_sum += v
            initial.psum += f
        initial.recompute_entropy()
        self.entropy_values: list[EntropyValues] = [
            copy(initial) for _ in range(self.indices)
        ]
        pass

    def do_ban(self, index: int, pattern: int) -> None:
        self.entropy_values[index].decrement(
            self.frequencies[pattern], self.p_logp[pattern]
        )

    def undo_ban(self, index: int, pattern: int) -> None:
        self.entropy_values[index].increment(
            self.frequencies[pattern], self.p_logp[pattern]
        )

    def init(self, wave_propagator: WavePropagator) -> None:
        self.local_init(
            wave_propagator.wave,
            wave_propagator.frequencies,
            wave_propagator.topology.mask,
        )
        wave_propagator.add_tracker(self)
        pass

    def local_init(
        self, wave: Wave | None, frequencies: list[float], mask: bitarray | None
    ) -> None:
        self.frequencies: list[float] = frequencies
        self.pattern_count: int = len(frequencies)
        self.mask: bitarray | None = mask

        if wave is None:
            raise Exception("No wave provided")

        self.wave: Wave = wave
        self.indices: int = wave.indices

        # Initialize p_logp
        # See the definition in EntropyValues
        self.p_logp: list[float] = [
            f * math.log1p(f) if f > 0 else 0.0 for f in self.frequencies
        ]

        self.entropy_values: list[EntropyValues] = []

        self.reset()

    def get_random_index(self, random_double: Callable[[], float]) -> int:
        """
        Finds the cells with minimal entropy (excluding 0, decided cells).

        Then picks one randomly.
        Returns -1 if every cell is decided.
        """
        return self.get_random_index_with_indicies(random_double, range(self.indices))

    def get_random_index_with_indicies(
        self, random_double: Callable[[], float], indices: Iterable[int]
    ) -> int:
        """
        Finds the cells with minimal entropy (excluding 0, decided cells).

        Then picks one randomly.
        Returns -1 if every cell is decided.
        """
        selected_index: int = -1
        min_entropy: float = float("inf")
        count_at_min_entropy: int = 0
        for i in indices:
            if self.mask is not None and not self.mask[i]:
                continue
            c = self.wave.get_pattern_count(i)
            e = self.entropy_values[i].entropy
            if c <= 1:
                continue
            elif e < min_entropy:
                count_at_min_entropy = 1
                min_entropy = e
            elif e == min_entropy:
                count_at_min_entropy += 1
        n = int(count_at_min_entropy * random_double())
        for i in indices:
            if self.mask is not None and not self.mask[i]:
                continue
            c = self.wave.get_pattern_count(i)
            e = self.entropy_values[i].entropy
            if c <= 1:
                continue
            elif e == min_entropy:
                if n == 0:
                    selected_index = i
                    break
                n -= 1
        return selected_index
