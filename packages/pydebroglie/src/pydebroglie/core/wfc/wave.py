from typing import Self

from bitarray import bitarray


class Wave:
    def __init__(self, pattern_count: int, indices: int) -> None:
        self.pattern_count: int = pattern_count
        self.indices: int = indices
        self.possibilities: bitarray = bitarray(indices * pattern_count)
        self.possibilities.setall(True)
        self.pattern_counts: list[int] = [pattern_count for _ in range(indices)]

    def get(self, index: int, pattern: int) -> bool:
        return bool(self.possibilities[index * self.pattern_count + pattern])