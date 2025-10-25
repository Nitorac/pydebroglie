from bitarray import bitarray


class Wave:
    """
    Wave is a fancy array that tracks various per-cell information.

    Most importantly, it tracks possibilities - which patterns are possible to put
    into which cells.
    It has no notion of cell adjacency, cells are just referred to by integer index.
    internal
    """

    def __init__(self, pattern_count: int, indices: int) -> None:
        self.pattern_count: int = pattern_count
        self.indices: int = indices
        # self.possibilities[index*patternCount + pattern] is true if we haven't
        # eliminated putting that pattern at that index.
        self.possibilities: bitarray = bitarray(indices * pattern_count)
        self.possibilities.setall(True)
        self.pattern_counts: list[int] = [pattern_count for _ in range(indices)]

    def get(self, index: int, pattern: int) -> bool:
        return bool(self.possibilities[index * self.pattern_count + pattern])

    def get_pattern_count(self, index: int) -> int:
        return self.pattern_counts[index]

    def remove_possibility(self, index: int, pattern: int) -> bool:
        if __debug__ and not self.get(index, pattern):
            raise ValueError(
                f"DEV ERROR: Should not happen (index={index}, pattern={pattern})"
            )
        self.possibilities[index * self.pattern_count + pattern] = False
        self.pattern_counts[index] -= 1
        return self.pattern_counts[index] == 0

    def add_possibility(self, index: int, pattern: int) -> None:
        if __debug__ and self.get(index, pattern):
            raise ValueError(
                f"DEV ERROR: Should not happen (index={index}, pattern={pattern})"
            )
        self.possibilities[index * self.pattern_count + pattern] = True
        self.pattern_counts[index] += 1

    def get_progress(self) -> float:
        return self.possibilities.count(False) / (self.pattern_count - 1) / self.indices
