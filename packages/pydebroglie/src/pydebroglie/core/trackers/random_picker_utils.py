from collections.abc import Callable

from pydebroglie.core.wfc.wave import Wave


class RandomPickerUtils:
    @staticmethod
    def get_random_possible_pattern(
        wave: Wave,
        random_double: Callable[[], float],
        index: int,
        frequencies: list[float],
        patterns: list[int] | None,
    ) -> int:
        pattern_count = len(frequencies)
        if patterns is None:
            patterns = list(range(pattern_count))
        s = 0.0
        for i in range(pattern_count):
            pattern = patterns[i]
            if wave.get(index, pattern):
                s += frequencies[i]
        r = random_double() * s
        for i in range(pattern_count):
            pattern = patterns[i]
            if wave.get(index, pattern):
                r -= frequencies[i]
                if r <= 0:
                    return pattern
        return patterns[len(patterns) - 1]
