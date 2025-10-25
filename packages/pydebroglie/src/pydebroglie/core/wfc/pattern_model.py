from dataclasses import dataclass


@dataclass(init=False)
class PatternModel:
    # propagator[pattern1][edgeLabel] contains all the patterns
    # that can be placed in next to pattern1 according to the
    # given edge label. NB: For grid topologies edge label
    # corresponds to the direction.
    propagator: list[list[list[int]]]

    # Stores the desired relative frequencies of each pattern
    frequencies: list[float]

    def pattern_count(self) -> int:
        return len(self.frequencies)
